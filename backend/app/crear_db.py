import sqlite3
from pathlib import Path

base_dir = Path(__file__).resolve().parent
base_dir.mkdir(parents=True, exist_ok=True)

ruta_db = base_dir / 'database.db'
conexion = sqlite3.connect(ruta_db)
cursor = conexion.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_trazabilidad TEXT UNIQUE,
    nombre TEXT NOT NULL,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    fecha_adquisicion TEXT NOT NULL,
    manual TEXT
)''')
conexion.commit()
conexion.close()
print("Tabla 'equipos' creada exitosamente en la base de datos.")