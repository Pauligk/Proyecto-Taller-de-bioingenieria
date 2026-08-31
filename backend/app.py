from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

from db import obtener_conexion, inicializar_base_de_datos
from algoritmos import procesar_triaje_equipos

app = Flask(__name__)

@app.route("/")
def panel_principal():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT e.*, COUNT(f.id) as cantidad_fallas
        FROM equipos e
        LEFT JOIN historial_fallas f ON e.id = f.equipo_id
        GROUP BY e.id
    """)
    filas = cursor.fetchall()
    conexion.close()
    
    equipos = procesar_triaje_equipos(filas)
    return render_template("index.html", equipos=equipos)

@app.route("/agregar_equipo", methods=["POST"])
def agregar_equipo():
    codigo = request.form["codigo"].strip()
    nombre = request.form["nombre"].strip()
    marca = request.form["marca"].strip()
    ubicacion = request.form["ubicacion"].strip()
    funcion = float(request.form.get("funcion", 5.0))
    aplicacion = float(request.form.get("aplicacion", 5.0))
    mantenimiento = float(request.form.get("mantenimiento", 3.0))
    manual = request.form.get("manual", "").strip()

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO equipos (codigo_trazabilidad, nombre, marca, ubicacion, puntaje_funcion, puntaje_aplicacion, puntaje_mantenimiento, manual_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (codigo, nombre, marca, ubicacion, funcion, aplicacion, mantenimiento, manual if manual else None))
        conexion.commit()
    except sqlite3.IntegrityError:
        pass  # Evita duplicación de código ANMAT
    finally:
        conexion.close()
        
    return redirect(url_for("panel_principal"))

@app.route("/equipo/<int:equipo_id>")
def detalle_equipo(equipo_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT * FROM equipos WHERE id = ?", (equipo_id,))
    equipo = cursor.fetchone()
    
    cursor.execute("SELECT * FROM historial_fallas WHERE equipo_id = ? ORDER BY id DESC", (equipo_id,))
    fallas = cursor.fetchall()
    conexion.close()
    
    return render_template("detalle.html", equipo=equipo, fallas=fallas)

@app.route("/equipo/<int:equipo_id>/reportar_falla", methods=["POST"])
def reportar_falla(equipo_id):
    usuario = request.form["usuario"].strip()
    tipo = request.form["tipo"].strip()
    descripcion = request.form["descripcion"].strip()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO historial_fallas (equipo_id, fecha_falla, usuario_reporta, tipo_mantenimiento, descripcion)
        VALUES (?, ?, ?, ?, ?)
    """, (equipo_id, fecha, usuario, tipo, descripcion))
    conexion.commit()
    conexion.close()
    
    return redirect(url_for("detalle_equipo", equipo_id=equipo_id))

@app.route("/eliminar/<int:id>")
def eliminar(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM historial_fallas WHERE equipo_id = ?", (id,))
    cursor.execute("DELETE FROM equipos WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()
    return redirect(url_for("panel_principal"))

if __name__ == "__main__":
    inicializar_base_de_datos()
    app.run(debug=True)