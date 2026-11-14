from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from db import *
from algoritmos import procesar_triaje_equipos

app = Flask(__name__)

@app.route("/")
def panel_principal():
    filas = obtener_equipos()
    equipos = procesar_triaje_equipos(filas)
    cantidad_mantenimiento = len(obtener_equipos_mantenimiento())
    return render_template("index.html", equipos=equipos, cantidad_mantenimiento=cantidad_mantenimiento)

@app.route("/agregar_equipo", methods=["POST"])
def agregar_equipo():
    datos = ( 
        request.form["codigo"].strip(),
        request.form.get("numero_serie", "").strip(),
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

@app.route("/equipo/<int:equipo_id>/cargar_intervencion", methods=["POST"])
def cargar_intervencion(equipo_id):
    insertar_intervencion(
        equipo_id,
        request.form["tipo_intervencion"].strip(),
        request.form["fecha_intervencion"].strip(),
        request.form["usuario_interviene"].strip(),
        request.form["area"].strip(),
        request.form["descripcion"].strip(),
        request.form["falla_solucionada"].strip(),
        request.form["repuestos_utilizados"].strip(),
        request.form["estado_final"].strip(),
        float(request.form["tiempo_intervencion"]),
        "Carga rápida desde modal" # Observaciones por defecto
    )
    return redirect(url_for("panel_principal"))

@app.route("/equipo/<int:equipo_id>")
def detalle_equipo(equipo_id):
    # Usamos la nueva función para traer el combo completo
    equipo, fallas, intervenciones = obtener_historia_completa(equipo_id)
    
    # Le enviamos las 3 cosas al HTML
    return render_template("detalle.html", equipo=equipo, fallas=fallas, intervenciones=intervenciones)

@app.route("/eliminar/<int:id>")
def eliminar(id):
    baja_total(id)
    return redirect(url_for("panel_principal"))

@app.route("/equipo/<int:id>/enviar_mantenimiento")
def enviar_a_mantenimiento(id):
    # Llama a tu función de db.py para cambiar el estado
    baja_mantenimiento_equipo(id)
    # Recarga la página principal
    return redirect(url_for("panel_principal"))

@app.route("/descartados")
def equipos_descartados():
    # Usamos la función de db.py para traer solo los descartados
    filas_baja = obtener_equipos_descartados() 
    # Se los mandamos a tu nueva pantalla HTML
    return render_template("descartados.html", equipos=filas_baja)

@app.route("/reportar_falla_general", methods=["POST"])
def reportar_falla_general():
    insertar_falla(
        int(request.form["equipo_id"]),
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        request.form["usuario"].strip(),
        request.form["tipo"].strip(),
        request.form["descripcion"].strip()
    )
    return redirect(url_for("panel_principal"))

@app.route("/cargar_intervencion_general", methods=["POST"])
def cargar_intervencion_general():
    insertar_intervencion(
        int(request.form["equipo_id"]),
        request.form["tipo_intervencion"].strip(),
        request.form["fecha_intervencion"].strip(),
        request.form["usuario_interviene"].strip(),
        request.form["area"].strip(),
        request.form["descripcion"].strip(),
        request.form["falla_solucionada"].strip(),
        request.form["repuestos_utilizados"].strip(),
        request.form["estado_final"].strip(),
        float(request.form["tiempo_intervencion"]),
        "Carga general desde panel maestro"
    )
    return redirect(url_for("panel_principal"))

@app.route("/en_mantenimiento")
def equipos_en_mantenimiento():
    # 1. Consultamos a la base de datos por los equipos en reparación
    filas_mantenimiento = obtener_equipos_mantenimiento()
    
    # 2. Enviamos esos datos a una nueva pantalla visual
    return render_template("mantenimiento.html", equipos=filas_mantenimiento)


 
 

@app.route("/equipo/<int:id>/restaurar_activo")
def restaurar_activo(id):
    restaurar_equipo_activo(id)
    return redirect(url_for("equipos_en_mantenimiento"))




if __name__ == "__main__":
    inicializar_base_de_datos()
    app.run(debug=True)