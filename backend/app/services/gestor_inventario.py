import sqlite3
from pathlib import Path

# Ubicación de la base de datos dentro de la misma carpeta
CARPETA_PROYECTO = Path(__file__).resolve().parent
RUTA_BASE_DATOS = CARPETA_PROYECTO / "cmms_hospital.db"

def obtener_conexion():
    """Crea la conexión a la base de datos y activa las claves foráneas."""
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion

def inicializar_base_de_datos():
    """Garantiza que las tablas existan antes de realizar cualquier operación."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # 1. Tabla de Equipos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_trazabilidad TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        marca TEXT NOT NULL,
        ubicacion TEXT NOT NULL,
        manual_url TEXT
    );
    """)

    # 2. Tabla de Historial de Fallas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial_fallas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipo_id INTEGER NOT NULL,
        fecha_falla TEXT NOT NULL,
        hora_falla TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        FOREIGN KEY (equipo_id) REFERENCES equipos (id)
    );
    """)

    conexion.commit()
    conexion.close()

# ==========================================
# 1. FUNCIONES PARA EQUIPOS
# ==========================================

def agregar_equipo(codigo: str, nombre: str, marca: str, ubicacion: str, manual_url: str = None):
    """Inserta un nuevo equipo en el inventario."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO equipos (codigo_trazabilidad, nombre, marca, ubicacion, manual_url)
            VALUES (?, ?, ?, ?, ?)
        """, (codigo, nombre, marca, ubicacion, manual_url))
        conexion.commit()
        print(f"\n✅ ¡Equipo '{nombre}' registrado con éxito!")
    except sqlite3.IntegrityError:
        print(f"\n⚠️ Error: Ya existe un equipo con el código '{codigo}'.")
    finally:
        conexion.close()

def listar_equipos():
    """Muestra en pantalla todos los equipos registrados."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, codigo_trazabilidad, nombre, marca, ubicacion FROM equipos")
    equipos = cursor.fetchall()
    conexion.close()

    print("\n--- 📋 LISTADO DE EQUIPOS BIOMÉDICOS ---")
    if not equipos:
        print("No hay equipos cargados en el sistema.")
    else:
        for eq in equipos:
            print(f"ID: {eq[0]} | Código: {eq[1]} | Equipo: {eq[2]} | Marca: {eq[3]} | Sala: {eq[4]}")
    print("----------------------------------------\n")

def eliminar_equipo(equipo_id: int):
    """Elimina un equipo y sus fallas asociadas de la base de datos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT nombre FROM equipos WHERE id = ?", (equipo_id,))
    equipo = cursor.fetchone()
    
    if equipo is None:
        print(f"\n⚠️ No se encontró ningún equipo con el ID {equipo_id}.")
        conexion.close()
        return

    cursor.execute("DELETE FROM historial_fallas WHERE equipo_id = ?", (equipo_id,))
    cursor.execute("DELETE FROM equipos WHERE id = ?", (equipo_id,))
    conexion.commit()
    conexion.close()
    print(f"\n🗑️ Equipo '{equipo[0]}' (ID {equipo_id}) eliminado correctamente.")

# ==========================================
# 2. FUNCIONES PARA HISTORIAL DE FALLAS
# ==========================================

def registrar_falla(equipo_id: int, fecha: str, hora: str, descripcion: str):
    """Agrega un registro de falla asociado a un equipo específico."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO historial_fallas (equipo_id, fecha_falla, hora_falla, descripcion)
            VALUES (?, ?, ?, ?)
        """, (equipo_id, fecha, hora, descripcion))
        conexion.commit()
        print(f"\n✅ Falla registrada para el equipo ID {equipo_id}.")
    except sqlite3.IntegrityError:
        print(f"\n⚠️ Error: El equipo con ID {equipo_id} no existe.")
    finally:
        conexion.close()

def listar_fallas_de_equipo(equipo_id: int):
    """Muestra todas las fallas registradas de un equipo."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, fecha_falla, hora_falla, descripcion 
        FROM historial_fallas 
        WHERE equipo_id = ?
    """, (equipo_id,))
    fallas = cursor.fetchall()
    conexion.close()

    print(f"\n--- ⚠️ HISTORIAL DE FALLAS (Equipo ID: {equipo_id}) ---")
    if not fallas:
        print("Este equipo no tiene fallas registradas.")
    else:
        for f in fallas:
            print(f"Falla ID: {f[0]} | Fecha: {f[1]} {f[2]} | Detalle: {f[3]}")
    print("---------------------------------------------------\n")

# ==========================================
# 3. MENÚ INTERACTIVO EN TERMINAL
# ==========================================

def menu_principal():
    # Creamos las tablas automáticamente al iniciar
    inicializar_base_de_datos()
    
    while True:
        print("\n=== SISTEMA DE GESTIÓN HOSPITALARIA (CMMS) ===")
        print("1.  Registrar nuevo equipo")
        print("2.  Ver todos los equipos")
        print("3.  Dar de baja / Eliminar un equipo")
        print("4.  Cargar reporte de falla")
        print("5.  Ver historial de fallas de un equipo")
        print("6.  Salir")
        
        opcion = input("Selecciona una opción (1-6): ").strip()

        if opcion == "1":
            codigo = input("Código ANMAT/Trazabilidad: ")
            nombre = input("Nombre del equipo: ")
            marca = input("Marca: ")
            ubicacion = input("Ubicación/Sala: ")
            manual = input("URL/Ruta manual (Enter para omitir): ")
            agregar_equipo(codigo, nombre, marca, ubicacion, manual if manual else None)

        elif opcion == "2":
            listar_equipos()

        elif opcion == "3":
            listar_equipos()
            id_eq = input("Ingresa el ID del equipo a eliminar: ")
            if id_eq.isdigit():
                eliminar_equipo(int(id_eq))

        elif opcion == "4":
            listar_equipos()
            id_eq = input("ID del equipo que falló: ")
            fecha = input("Fecha (YYYY-MM-DD): ")
            hora = input("Hora (HH:MM): ")
            desc = input("Descripción de la falla: ")
            if id_eq.isdigit():
                registrar_falla(int(id_eq), fecha, hora, desc)

        elif opcion == "5":
            id_eq = input("ID del equipo a consultar: ")
            if id_eq.isdigit():
                listar_fallas_de_equipo(int(id_eq))

        elif opcion == "6":
            print("Saliendo del gestor...")
            break
        else:
            print("Opción inválida. Intenta nuevamente.")

if __name__ == "__main__":
    menu_principal()