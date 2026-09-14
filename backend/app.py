from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from db import *
from algoritmos import procesar_triaje_equipos

app = Flask(__name__)

@app.route("/")
def panel_principal():
    filas = obtener_equipos()
    equipos = procesar_triaje_equipos(filas)
    return render_template("index.html", equipos=equipos)

@app.route("/agregar_equipo", methods=["POST"])
def agregar_equipo():
    datos = ( 
        request.form["codigo"].strip(),
        request.form["nombre"].strip(),
        request.form["marca"].strip(),
        request.form["ubicacion"].strip(),
        float(request.form.get("funcion", 5.0)),
        float(request.form.get("aplicacion", 5.0)),
        float(request.form.get("mantenimiento", 3.0)),
        request.form.get("manual", "").strip(),
    )

    insertar_equipo(datos)
        
    return redirect(url_for("panel_principal"))

@app.route("/equipo/<int:equipo_id>")
def detalle_equipo(equipo_id):
    equipo, fallas = obtener_equipo_con_fallas(equipo_id)
    
    return render_template("detalle.html", equipo=equipo, fallas=fallas)

@app.route("/equipo/<int:equipo_id>/reportar_falla", methods=["POST"])
def reportar_falla(equipo_id):
    insertar_falla(
        equipo_id,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        request.form["usuario"].strip(),
        request.form["tipo"].strip(),
        request.form["descripcion"].strip(),
        
    )

    return redirect(url_for("detalle_equipo", equipo_id=equipo_id))

@app.route("/eliminar/<int:id>")
def eliminar(id):
    dar_de_baja_equipo(id)
    return redirect(url_for("panel_principal"))

@app.route("/descartados")
def equipos_descartados():
    # Usamos la función de db.py para traer solo los descartados
    filas_baja = obtener_equipos_descartados() 
    # Se los mandamos a tu nueva pantalla HTML
    return render_template("descartados.html", equipos=filas_baja)

if __name__ == "__main__":
    inicializar_base_de_datos()
    app.run(debug=True)