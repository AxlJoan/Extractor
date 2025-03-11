import sqlite3
import pandas as pd
import mysql.connector
import os

# Rutas de la base de datos wa.db
wa_db_path = '/sdcard/wa.db'  # Ruta original
wa_db_backup_path = '/storage/emulated/0/WhatsApp/Databases/wa.db'  # Ruta de respaldo

# Conexión a wa.db y consulta de la tabla "wa_contacts"
try:
    with sqlite3.connect(wa_db_path) as con:
        query = "SELECT jid FROM wa_contacts"
        contacts_df = pd.read_sql_query(query, con)
        print("Consulta exitosa en la ruta original.")
except sqlite3.Error as e:
    print(f"Error conectando a la base de datos en la ruta {wa_db_path}: {e}")
    print("Intentando con la nueva ruta...")
    try:
        with sqlite3.connect(wa_db_backup_path) as con:
            query = "SELECT jid FROM wa_contacts"
            contacts_df = pd.read_sql_query(query, con)
            print("Consulta exitosa en la ruta de respaldo.")
    except sqlite3.Error as e:
        print(f"Error conectando a la base de datos en la nueva ruta {wa_db_backup_path}: {e}")
        exit(1)

# Contar el número total de contactos únicos (números) usando la columna "jid"
total_numbers = len(contacts_df['jid'].unique())
print(f"Cantidad total de números: {total_numbers}")

# Datos de conexión a MySQL
MYSQL_USER = "admin"
MYSQL_PASS = "S3gur1d4d2025"
MYSQL_HOST = "158.69.26.160"
MYSQL_DB = "data_wa"

try:
    mysql_con = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB
    )
    with mysql_con.cursor() as cursor:
        # Crear la tabla si no existe, usando UNIQUE para evitar duplicados.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS total_participantes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            group_name VARCHAR(255),
            total INT,
            UNIQUE KEY unique_group (group_name)
        )
        """)
        
        # Actualizar o insertar el total de números con un identificador fijo "total_contactos"
        add_total = """
        INSERT INTO total_participantes (group_name, total)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE total = VALUES(total);
        """
        data = ("total_contactos", total_numbers)
        cursor.execute(add_total, data)
        mysql_con.commit()
        print("Datos actualizados en MySQL correctamente.")
except mysql.connector.Error as e:
    print(f"Error en MySQL: {e}")
finally:
    if 'mysql_con' in locals():
        mysql_con.close()
