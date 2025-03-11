import sqlite3
import pandas as pd
import mysql.connector
import os
import emoji
from datetime import datetime

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
        }
        with open(config_file_path, 'w') as file:
            for key, value in config.items():
                file.write(f'{key}={value}\n')
    return config

config = get_or_prompt_config()

# Conexión a SQLite (WhatsApp)
msgstore_path = '/sdcard/msgstore.db'
wa_db_path = '/sdcard/wa.db'
try:
    with sqlite3.connect(msgstore_path) as con:
        usuarios = pd.read_sql_query("SELECT * from 'jid'", con)
        msg = pd.read_sql_query("SELECT * from message", con)
except sqlite3.Error as e:
    print(f"Error en SQLite: {e}")
    exit(1)

try:
    with sqlite3.connect(wa_db_path) as con1:
        contacts = pd.read_sql_query("SELECT * from wa_contacts", con1)
except sqlite3.Error as e:
    print(f"Error en SQLite: {e}")
    exit(1)

# Procesamiento de datos
usuarios['user'] = usuarios['user'].astype(str).str[3:]
usuarios['server'] = usuarios['server'].apply(lambda x: 'grupo' if x.endswith('.us') else 'otro')

msg = msg.loc[:, ['chat_row_id', 'timestamp', 'received_timestamp', 'text_data', 'from_me']].dropna(subset=['text_data'])
msg['timestamp'] = pd.to_datetime(msg['timestamp'], unit='ms')
msg['received_timestamp'] = pd.to_datetime(msg['received_timestamp'], unit='ms')

def remove_emojis(text):
    return emoji.replace_emoji(text, replace='') if text else text

msg['text_data'] = msg['text_data'].apply(remove_emojis)
msg['cliente'] = config['cliente']
msg['estado'] = config['estado']
msg['municipio'] = config['municipio']

# Obtención del número de participantes por grupo
participantes_por_grupo = usuarios[usuarios['server'] == 'grupo'].groupby('user').size().reset_index(name='total_participantes')

# Conexión a MySQL
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
        # Crear tabla principal
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS extraccion4 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_row_id INT,
            timestamp DATETIME,
            received_timestamp DATETIME,
            text_data TEXT,
            from_me BOOLEAN,
            number2 VARCHAR(255),
            cliente VARCHAR(255),
            estado VARCHAR(255),
            municipio VARCHAR(255),
            UNIQUE KEY unique_message (chat_row_id, timestamp)
        )
        """)
        
        # Insertar datos en extraccion4
        add_message = """
        INSERT IGNORE INTO extraccion4 (chat_row_id, timestamp, received_timestamp, text_data, from_me, number2, cliente, estado, municipio)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.executemany(add_message, msg.to_records(index=False).tolist())
        mysql_con.commit()
        
        # Crear tabla de participantes por grupo
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS total_participantes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            group_name VARCHAR(255) UNIQUE,
            total_participantes INT
        )
        """)
        
        # Insertar o actualizar participantes por grupo
        add_participants = """
        INSERT INTO total_participantes (group_name, total_participantes)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE total_participantes = VALUES(total_participantes);
        """
        cursor.executemany(add_participants, participantes_por_grupo.to_records(index=False).tolist())
        mysql_con.commit()
        
        # Eliminar grupos que ya no existen en la extracción actual
        cursor.execute("""
        DELETE FROM total_participantes 
        WHERE group_name NOT IN (SELECT DISTINCT user FROM usuarios WHERE server = 'grupo')
        """)
        mysql_con.commit()
except mysql.connector.Error as e:
    print(f"Error en MySQL: {e}")
finally:
    mysql_con.close()

print("Datos subidos y sincronizados correctamente.")
