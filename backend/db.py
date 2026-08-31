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
    
    # 1. Tabla de Inventario de Equipos Biomédicos
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