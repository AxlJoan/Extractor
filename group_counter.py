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
        # Verificar si la columna cliente existe, si no, agregarla
        cursor.execute("SHOW COLUMNS FROM total_participantes LIKE 'cliente';")
        column_exists = cursor.fetchone()
        if not column_exists:
            cursor.execute("ALTER TABLE total_participantes ADD COLUMN cliente VARCHAR(255);")
            mysql_con.commit()
            print("Columna 'cliente' añadida a total_participantes.")
        
        # Asegurarse de que la tabla existe, en caso de que no se haya creado previamente
        cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS total_participantes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            group_name VARCHAR(255),
            total INT,
            cliente VARCHAR(255),
            UNIQUE KEY unique_cliente_group (cliente, group_name)
        )
        """)
        
        # Actualizar o insertar el total de contactos con el cliente
        add_total = """
        INSERT INTO total_participantes (group_name, total, cliente)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE total = VALUES(total);
        """
        data = ("total_contactos", total_numbers, cliente)
        
        cursor.execute(add_total, data)
        mysql_con.commit()
        print(f"Datos actualizados para cliente {cliente} en MySQL correctamente.")
except mysql.connector.Error as e:
    print(f"Error en MySQL: {e}")
finally:
    if 'mysql_con' in locals():
        mysql_con.close()
