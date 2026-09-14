import sqlite3
from pathlib import Path

RUTA_BD = Path(__file__).resolve().parent / "cmms_hospital.db"

def obtener_conexion():
    """Establece la conexión a SQLite y activa el control de claves foráneas."""
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion

def inicializar_base_de_datos():
    """Crea las tablas relacionales si no existen."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # 1. Tabla de Inventario de Equipos Biomédicos (CON LA COLUMNA ESTADO)
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
        manual_url TEXT,
        estado TEXT DEFAULT 'Activo'
    );
    """)

    # 2. Tabla de Historia Clínica Técnica y Reporte de Fallas
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

def obtener_equipos():
    """Recupera SOLO los equipos activos de la db"""
    conexion = obtener_conexion()
    try:
        return conexion.execute("""
        SELECT e.*, COUNT(f.id) AS cantidad_fallas
        FROM equipos e
        LEFT JOIN historial_fallas f ON e.id = f.equipo_id
        WHERE e.estado = 'Activo'
        GROUP BY e.id
        """).fetchall()
    finally:
        conexion.close()

def insertar_equipo(datos):
    """Inserta un equipo en la db"""
    conexion = obtener_conexion()
    try:
        conexion.execute("""
        INSERT INTO equipos (
            codigo_trazabilidad, nombre, marca, ubicacion, 
            puntaje_funcion, puntaje_aplicacion, puntaje_mantenimiento, manual_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, datos)
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexion.close()

def obtener_equipo_con_fallas(equipo_id):
    """Obtiene el historial de un equipo"""
    conexion = obtener_conexion()
    try:
        equipo = conexion.execute("SELECT * FROM equipos WHERE id = ?", (equipo_id,)).fetchone()
        fallas = conexion.execute("SELECT * FROM historial_fallas WHERE equipo_id = ? ORDER BY id DESC", (equipo_id,)).fetchall()
        return equipo, fallas
    finally:
        conexion.close()

def insertar_falla(equipo_id, fecha, usuario, tipo, descripcion):
    """Registra un evento"""
    conexion = obtener_conexion()
    try:
        conexion.execute("""
            INSERT INTO historial_fallas (equipo_id, fecha_falla, usuario_reporta, tipo_mantenimiento, descripcion)
            VALUES (?, ?, ?, ?, ?)
        """, (equipo_id, fecha, usuario, tipo, descripcion))
        conexion.commit()
    finally:
        conexion.close()

def dar_de_baja_equipo(equipo_id): 
    """Cambia el estado del equipo a 'Descartado' (Borrado lógico)"""
    conexion = obtener_conexion()
    try:
        conexion.execute("UPDATE equipos SET estado = 'Descartado' WHERE id = ?", (equipo_id,))
        conexion.commit()
    finally:
        conexion.close()

def obtener_equipos_descartados():
    """Recupera los equipos que fueron dados de baja"""
    conexion = obtener_conexion()
    try:
        return conexion.execute("""
        SELECT e.*, COUNT(f.id) AS cantidad_fallas
        FROM equipos e
        LEFT JOIN historial_fallas f ON e.id = f.equipo_id
        WHERE e.estado = 'Descartado'
        GROUP BY e.id
        """).fetchall()
    finally:
        conexion.close()