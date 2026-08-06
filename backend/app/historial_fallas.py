import sqlite3
from pathlib import Path

# 1. Le decimos a Python dónde está nuestra base de datos principal
CARPETA_PROYECTO = Path(__file__).resolve().parent
RUTA_BASE_DATOS = CARPETA_PROYECTO / "database.db"

# 2. Conectamos y creamos el cursor (¡esto es lo que te faltaba!)
conexion = sqlite3.connect(RUTA_BASE_DATOS)
cursor = conexion.cursor()

# 3. Definimos los datos de la falla a registrar
falla_nueva = (
    1,                                                  # equipo_id (Vínculo con el ID 1)
    "2026-08-06",                                       # fecha_falla
    "14:30",                                            # hora_falla
    "Ruptura en el cable de derivaciones del paciente"  # descripcion
)

try:
    # 4. Insertamos la falla
    cursor.execute("""
    INSERT INTO historial_fallas (equipo_id, fecha_falla, hora_falla, descripcion)
    VALUES (?, ?, ?, ?)
    """, falla_nueva)

    # 5. ¡IMPORTANTE! Guardamos los cambios en el archivo .db
    conexion.commit()
    print("🎉 ¡Falla registrada y vinculada al equipo ID 1 con éxito!")

except sqlite3.OperationalError as e:
    print(f"⚠️ Ocurrió un problema (Asegúrate de que la tabla 'historial_fallas' exista): {e}")

finally:
    # 6. Cerramos la conexión para no dejar el archivo bloqueado
    conexion.close()