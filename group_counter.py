import sqlite3
import pandas as pd
import mysql.connector
import os

# Leer cliente desde config.txt
config_path = "config.txt"
cliente = None

if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("cliente="):  # Buscar la línea con cliente=
                cliente = line.split("=")[1].strip()  # Extraer el valor y limpiar espacios
                break
else:
    print("Error: No se encontró config.txt")
    exit(1)

if not cliente:
    print("Error: No se pudo leer el cliente desde config.txt")
    exit(1)

print(f"Cliente leído: {cliente}")

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

# Agregar la fecha y hora actual
from datetime import datetime
import mysql.connector

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
        # Eliminar registros antiguos del mismo cliente antes de insertar el nuevo
        delete_old = """
        DELETE FROM total_participantes
        WHERE cliente = %s AND fecha_subida < %s;
        """
        cursor.execute(delete_old, (cliente, fecha_actual))
        mysql_con.commit()
        print(f"Registros antiguos eliminados para el cliente {cliente}.")

        # Insertar nuevo registro con la fecha actual
        insert_new = """
        INSERT INTO total_participantes (group_name, total, cliente, fecha_subida)
        VALUES (%s, %s, %s, %s);
        """
        data = ("total_contactos", total_numbers, cliente, fecha_actual)
        cursor.execute(insert_new, data)
        mysql_con.commit()
        print(f"Datos insertados para el cliente {cliente} con fecha {fecha_actual}.")
except mysql.connector.Error as e:
    print(f"Error en MySQL: {e}")
finally:
    if 'mysql_con' in locals():
        mysql_con.close()
