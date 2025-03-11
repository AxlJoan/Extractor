import sqlite3
import pandas as pd
import mysql.connector
import os

config_file_path = 'config.txt'

def get_or_prompt_config():
    """Lee la configuración de un archivo o la solicita al usuario."""
    if os.path.isfile(config_file_path) and os.path.getsize(config_file_path) > 0:
        with open(config_file_path, 'r') as file:
            config = {line.split('=')[0]: line.split('=')[1].strip() for line in file if line.strip()}
    else:
        print("Bienvenido, configuraremos algunos detalles antes de empezar.")
        config = {
            'cliente': input('Ingrese el nombre del cliente: ').strip(),
            'estado': input('Ingrese el nombre del estado: ').strip(),
            'municipio': input('Ingrese el nombre del municipio: ').strip(),
            'total_contactos': '0'  # Se inicializa en 0
        }
        with open(config_file_path, 'w') as file:
            for key, value in config.items():
                file.write(f'{key}={value}\n')
    return config

def save_config(config):
    """Guarda la configuración actualizada en el archivo."""
    with open(config_file_path, 'w') as file:
        for key, value in config.items():
            file.write(f'{key}={value}\n')

# Leer configuración
config = get_or_prompt_config()

# Rutas de la base de datos wa.db
wa_db_path = '/sdcard/wa.db'
wa_db_backup_path = '/storage/emulated/0/WhatsApp/Databases/wa.db'

# Conectar y contar contactos
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
            contacts_df = pd.read_sql_query(query, con)
            print("Consulta exitosa en la ruta de respaldo.")
    except sqlite3.Error as e:
        print(f"Error conectando a {wa_db_backup_path}: {e}")
        exit(1)

# Actualizar el total de contactos
total_numbers = len(contacts_df['jid'].unique())
config['total_contactos'] = str(total_numbers)  # Convertir a string para guardarlo
save_config(config)

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
        # Crear tabla si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS total_participantes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            group_name VARCHAR(255),
            total INT,
            UNIQUE KEY unique_group (group_name)
        )
        """)

        # Insertar o actualizar el total de contactos
        add_total = """
        INSERT INTO total_participantes (group_name, total)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE total = VALUES(total);
        """
        data = ("total_contactos", total_numbers)
        cursor.execute(add_total, data)
        mysql_con.commit()

except mysql.connector.Error as e:
    print(f"Error conectando a MySQL: {e}")
finally:
    mysql_con.close()

print("Datos subidos con éxito.")
