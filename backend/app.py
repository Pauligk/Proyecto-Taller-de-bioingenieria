from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
RUTA_BD = Path(__file__).resolve().parent / "cmms_hospital.db"

def obtener_conexion():
    """Establece la conexion a SQLite y activa el control de claves foraneas."""
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion

def inicializar_base_de_datos():
    """Garantiza la creacion de las tablas relacionales para inventario e historia clinica tecnica."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # 1. Tabla de Equipos Biomedicos (Parametros del Modelo Smith)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_trazabilidad TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        marca TEXT NOT NULL,
        ubicacion TEXT NOT NULL,
        puntaje_funcion REAL DEFAULT 5.0,
        puntaje_aplicacion REAL DEFAULT 5.0,
        puntaje_mantenimiento REAL DEFAULT 3.0,
        manual_url TEXT
    );
    """)

    # 2. Tabla de Historia Clinica Tecnica y Reportes de Fallas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial_fallas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipo_id INTEGER NOT NULL,
        fecha_falla TEXT NOT NULL,
        usuario_reporta TEXT NOT NULL,
        tipo_mantenimiento TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        FOREIGN KEY (equipo_id) REFERENCES equipos (id) ON DELETE CASCADE
    );
    """)
    conexion.commit()
    conexion.close()

# ==========================================
# RUTAS Y CONTROLADORES
# ==========================================

@app.route("/")
def panel_principal():
    """Calcula la criticidad EM y lista los equipos ordenados por triaje clinico."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT e.*, COUNT(f.id) as cantidad_fallas
        FROM equipos e
        LEFT JOIN historial_fallas f ON e.id = f.equipo_id
        GROUP BY e.id
    """)
    filas = cursor.fetchall()
    
    equipos_procesados = []
    for fila in filas:
        eq = dict(fila)
        # Algoritmo EM: Funcion + Aplicacion + Mantenimiento + (Fallas * 2.0)
        puntaje_historia = eq["cantidad_fallas"] * 2.0
        em = eq["puntaje_funcion"] + eq["puntaje_aplicacion"] + eq["puntaje_mantenimiento"] + puntaje_historia
        eq["indice_em"] = em
        
        # Ponderacion de triaje tecnico
        if em >= 16:
            eq["prioridad"] = "ALTA"
            eq["color_badge"] = "danger"
        elif em >= 12:
            eq["prioridad"] = "MEDIA"
            eq["color_badge"] = "warning"
        else:
            eq["prioridad"] = "BAJA"
            eq["color_badge"] = "success"
            
        equipos_procesados.append(eq)
        
    # Orden descendente por urgencia tecnica (triaje)
    equipos_procesados.sort(key=lambda x: x["indice_em"], reverse=True)
    conexion.close()
    
    return render_template("index.html", equipos=equipos_procesados)

@app.route("/agregar_equipo", methods=["POST"])
def agregar_equipo():
    """Registra un nuevo activo con sus factores de riesgo iniciales."""
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
        pass
    finally:
        conexion.close()
        
    return redirect(url_for("panel_principal"))

@app.route("/equipo/<int:equipo_id>")
def detalle_equipo(equipo_id):
    """Muestra la ficha tecnica individual y el historial cronologico de averias."""
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
    """Agrega una intervencion o reporte de falla a la historia clinica del dispositivo."""
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
    """Elimina el activo y sus fallas vinculadas."""
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