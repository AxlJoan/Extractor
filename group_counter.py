import sqlite3
import pandas as pd
import mysql.connector
import os

# Rutas de la base de datos wa.db (mismo formato que en tu código)
wa_db_path = '/sdcard/wa.db'  # Ruta original
wa_db_backup_path = '/storage/emulated/0/WhatsApp/Databases/wa.db'  # Nueva ruta

# Conexión a wa.db (usando la misma estructura que en tu código)
try:
    with sqlite3.connect(wa_db_path) as con:
        # Se asume que la tabla que tiene el conteo se llama "group_membership_count"
        # y que sus columnas son "jid_row_id" y "member_count". Además, se une con
        # wa_group_descriptions para considerar sólo grupos existentes.
        query = """
        SELECT g.jid_row_id AS group_id, g.member_count 
        FROM group_membership_count g
        JOIN wa_group_descriptions d ON d.jid = g.jid_row_id
        """
        group_members = pd.read_sql_query(query, con)
except sqlite3.Error as e:
    print(f"Error conectando a la base de datos en la ruta {wa_db_path}: {e}")
    print("Intentando con la nueva ruta...")
    try:
        with sqlite3.connect(wa_db_backup_path) as con:
            query = """
            SELECT g.jid_row_id AS group_id, g.member_count 
            FROM group_membership_count g
            JOIN wa_group_descriptions d ON d.jid = g.jid_row_id
            """
            group_members = pd.read_sql_query(query, con)
    except sqlite3.Error as e:
        print(f"Error conectando a la base de datos en la nueva ruta {wa_db_backup_path}: {e}")
        exit(1)

# Eliminar duplicados por grupo (por si acaso)
group_members = group_members.drop_duplicates(subset='group_id')

# Sumar la cantidad total de participantes entre los grupos existentes
total_participants = group_members['member_count'].sum()
print(f"Cantidad total de participantes: {total_participants}")

# (Opcional) Actualizar los datos en MySQL
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
        # Crear la tabla si no existe, usando UNIQUE para evitar duplicados
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS total_participantes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            group_name VARCHAR(255),
            total INT,
            UNIQUE KEY unique_group (group_name)
        )
        """)
        
        # Insertar/actualizar cada grupo con su cantidad de participantes
        add_participants = """
        INSERT INTO total_participantes (group_name, total) 
        VALUES (%s, %s) 
        ON DUPLICATE KEY UPDATE total = VALUES(total);
        """
        # Se usa el group_id como identificador del grupo
        participant_data = [(row['group_id'], row['member_count']) for index, row in group_members.iterrows()]
        if participant_data:
            cursor.executemany(add_participants, participant_data)
            mysql_con.commit()
            print("Datos de grupos actualizados en MySQL.")
        else:
            print("No se encontraron datos de participantes para actualizar en MySQL.")
except mysql.connector.Error as e:
    print(f"Error en MySQL: {e}")
finally:
    if 'mysql_con' in locals():
        mysql_con.close()
