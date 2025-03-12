import os
import sqlite3
import pandas as pd
import mysql.connector
from datetime import datetime

# -------------------------
# 1. Leer configuración
# -------------------------
config_file_path = 'config.txt'

def get_config():
    config = {}
    if os.path.exists(config_file_path):
        with open(config_file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    config[key.strip()] = val.strip()
    else:
        print("Error: No se encontró config.txt")
        exit(1)
    return config

config = get_config()
cliente = config.get("cliente", None)
if not cliente:
    print("Error: No se pudo leer 'cliente' desde config.txt")
    exit(1)
print(f"Cliente leído: {cliente}")

# -------------------------
# 2. Conectar a wa.db y contar contactos
# -------------------------
wa_db_path = '/sdcard/wa.db'  # Ruta original
wa_db_backup_path = '/storage/emulated/0/WhatsApp/Databases/wa.db'  # Ruta de respaldo

try:
    with sqlite3.connect(wa_db_path) as con:
        query = "SELECT jid FROM wa_contacts"
        contacts_df = pd.read_sql_query(query, con)
        print("Consulta exitosa en la ruta original.")
except sqlite3.Error as e:
    print(f"Error conectando a {wa_db_path}: {e}")
    print("Intentando con la nueva ruta...")
    try:
        with sqlite3.connect(wa_db_backup_path) as con:
            query = "SELECT jid FROM wa_contacts"
            contacts_df = pd.read_sql_query(query, con)
            print("Consulta exitosa en la ruta de respaldo.")
    except sqlite3.Error as e:
        print(f"Error conectando a {wa_db_backup_path}: {e}")
        exit(1)

# Contar el total de contactos únicos en wa_contacts
total_numbers = len(contacts_df['jid'].unique())
print(f"Cantidad total de números: {total_numbers}")

# -------------------------
# 3. Conectar a MySQL y actualizar total_participantes
# -------------------------
MYSQL_USER = "admin"
MYSQL_PASS = "S3gur1d4d2025"
MYSQL_HOST = "158.69.26.160"
MYSQL_DB = "data_wa"

# Obtener la fecha y hora actual en formato MySQL
fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

try:
    mysql_con = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB
    )
    with mysql_con.cursor() as cursor:
        # Asegurar que la tabla total_participantes existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS total_participantes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_name VARCHAR(255),
                total INT,
                cliente VARCHAR(255),
                fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        mysql_con.commit()
        
        # Insertar un nuevo registro con la fecha actual
        insert_new = """
            INSERT INTO total_participantes (group_name, total, cliente, fecha_subida)
            VALUES (%s, %s, %s, %s)
        """
        data = ("total_contactos", total_numbers, cliente, fecha_actual)
        cursor.execute(insert_new, data)
        mysql_con.commit()
        print(f"Datos insertados para el cliente {cliente} con fecha {fecha_actual}.")
        
        # Eliminar los registros antiguos para ese cliente (con fecha menor a la fecha actual)
        delete_old = """
            DELETE FROM total_participantes
            WHERE cliente = %s AND fecha_subida < %s;
        """
        cursor.execute(delete_old, (cliente, fecha_actual))
        mysql_con.commit()
        print(f"Registros antiguos eliminados para el cliente {cliente}.")
        
except mysql.connector.Error as e:
    print(f"Error en MySQL: {e}")
finally:
    if 'mysql_con' in locals():
        mysql_con.close()

print("Proceso de conteo y actualización completado.")
