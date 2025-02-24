import sqlite3
import pandas as pd
from datetime import datetime
import emoji
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
        }
        with open(config_file_path, 'w') as file:
            for key, value in config.items():
                file.write(f'{key}={value}\n')
    return config

# Uso de la función para obtener la configuración
config = get_or_prompt_config()

# Conexión y lectura de la base de datos msgstore.db (con verificación de la existencia del archivo)
msgstore_path = '/sdcard/msgstore.db'  # Ruta original
backup_path = '/storage/emulated/0/WhatsApp/Databases/msgstore.db'  # Nueva ruta

# Intentar abrir la base de datos msgstore.db en la ruta original
try:
    with sqlite3.connect(msgstore_path) as con:
        try:
            chv = pd.read_sql_query("SELECT * FROM chat_view", con)
            print(chv.head())
        except pd.io.sql.DatabaseError:
            chv = None  # En caso de que el query no devuelva resultados

        usuarios = pd.read_sql_query("SELECT * from 'jid'", con)
        msg = pd.read_sql_query("SELECT * from message", con)
except sqlite3.Error as e:
    print(f"Error conectando a la base de datos en la ruta {msgstore_path}: {e}")
    print("Intentando con la nueva ruta...")

    # Intentar abrir la base de datos en la nueva ruta si no se pudo acceder a la ruta original
    try:
        with sqlite3.connect(backup_path) as con:
            chv = pd.read_sql_query("SELECT * FROM chat_view", con)
            print(chv.head())

            usuarios = pd.read_sql_query("SELECT * from 'jid'", con)
            msg = pd.read_sql_query("SELECT * from message", con)
    except sqlite3.Error as e:
        print(f"Error conectando a la base de datos en la nueva ruta {backup_path}: {e}")
        exit(1)

# Conexión y lectura de la base de datos wa.db
wa_db_path = '/sdcard/wa.db'  # Ruta original
wa_db_backup_path = '/storage/emulated/0/WhatsApp/Databases/wa.db'  # Nueva ruta

# Intentar abrir la base de datos wa.db en la ruta original
try:
    with sqlite3.connect(wa_db_path) as con1:
        contacts = pd.read_sql_query("SELECT * from wa_contacts", con1)
        contacts['jid'] = contacts['jid'].str.split('@').str[0]

        descriptions = pd.read_sql_query("SELECT * FROM wa_group_descriptions", con1)
        descriptions['jid'] = descriptions['jid'].str.split('@').str[0]

        names = pd.read_sql_query("SELECT * from wa_vnames", con1)
        names['jid'] = names['jid'].str.split('@').str[0]
except sqlite3.Error as e:
    print(f"Error conectando a la base de datos en la ruta {wa_db_path}: {e}")
    print("Intentando con la nueva ruta...")

    # Intentar abrir la base de datos en la nueva ruta si no se pudo acceder a la ruta original
    try:
        with sqlite3.connect(wa_db_backup_path) as con1:
            contacts = pd.read_sql_query("SELECT * from wa_contacts", con1)
            contacts['jid'] = contacts['jid'].str.split('@').str[0]

            descriptions = pd.read_sql_query("SELECT * FROM wa_group_descriptions", con1)
            descriptions['jid'] = descriptions['jid'].str.split('@').str[0]

            names = pd.read_sql_query("SELECT * from wa_vnames", con1)
            names['jid'] = names['jid'].str.split('@').str[0]
    except sqlite3.Error as e:
        print(f"Error conectando a la base de datos en la nueva ruta {wa_db_backup_path}: {e}")
        exit(1)

# Procesamiento de datos
usuarios['user'] = usuarios['user'].astype(str).str[3:]
usuarios['server'] = usuarios['server'].apply(lambda x: 'celular' if x.endswith('.net') else ('grupo' if x.endswith('.us') else 'otro'))

# Pre-procesamiento de msg
msg = msg.loc[:, ['chat_row_id', 'timestamp', 'received_timestamp', 'text_data', 'from_me']]
msg = msg.dropna(subset=['text_data'])  # Eliminar filas donde text_data es NaN
msg['timestamp'] = pd.to_datetime(msg['timestamp'], unit='ms')
msg['received_timestamp'] = pd.to_datetime(msg['received_timestamp'], unit='ms')

#def mapping(id):
    #phone = chv.loc[chv['_id'] == id, 'raw_string_jid'].iloc[0]
    #return phone.split('@')[0]

def mapping2(id):
    return usuarios.loc[usuarios['_id'] == id, 'user'].iloc[0]

def mapping3(id):
    return usuarios.loc[usuarios['_id'] == id, 'server'].iloc[0]

def mapping4(id):
    return usuarios.loc[usuarios['_id'] == id, 'device'].iloc[0]

def mapping5(id):
    return chv.loc[chv['_id'] == id, 'subject'].iloc[0]

#msg['number'] = msg['chat_row_id'].apply(mapping)
msg['number2'] = msg['chat_row_id'].apply(mapping2)
msg = pd.merge(msg, contacts[['jid', 'status']], left_on='number2', right_on='jid', how='left').drop('jid', axis=1)
msg = pd.merge(msg, names[['jid', 'verified_name']], left_on='number2', right_on='jid', how='left').drop('jid', axis=1)
msg['server'] = msg['chat_row_id'].apply(mapping3)
msg['device'] = msg['chat_row_id'].apply(mapping4)
msg['group'] = msg['chat_row_id'].apply(mapping5)
msg = pd.merge(msg, descriptions[['jid', 'description']], left_on='number2', right_on='jid', how='left').drop('jid', axis=1)

# Reemplazar NaN por None para los campos enriquecidos
msg = msg.where(pd.notnull(msg), None)

def remove_emojis(text):
    """Elimina emojis de un texto si no es None."""
    if text is None:
        return text
    return emoji.replace_emoji(text, replace='')

msg['text_data'] = msg['text_data'].apply(remove_emojis)
msg['description'] = msg['description'].apply(remove_emojis)
msg['group'] = msg['group'].apply(remove_emojis)

# Asegurarse de que las fechas están en el formato correcto
msg['timestamp'] = pd.to_datetime(msg['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
msg['received_timestamp'] = pd.to_datetime(msg['received_timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

# Añadir configuración al DataFrame
msg['cliente'] = config['cliente']
msg['estado'] = config['estado']
msg['municipio'] = config['municipio']

# Guardar datos en un archivo CSV
csv_file_path = 'messages_processed.csv'
msg.to_csv(csv_file_path, index=False)

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
        # Crear la tabla en MySQL si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS extraccion4 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_row_id INT,
            timestamp DATETIME,
            received_timestamp DATETIME,
            text_data TEXT,
            from_me BOOLEAN,
            number2 VARCHAR(255),
            status VARCHAR(255),
            verified_name VARCHAR(255),
            server VARCHAR(255),
            device VARCHAR(255),
            group_name VARCHAR(255),
            description TEXT,
            cliente VARCHAR(255),
            estado VARCHAR(255),
            municipio VARCHAR(255)
        )
        """)
        
        # Preparar la consulta SQL para insertar los datos
        add_message = """
        INSERT INTO extraccion4
        (chat_row_id, timestamp, received_timestamp, text_data, from_me, number2, status, verified_name, server, device, group_name, description, cliente, estado, municipio) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        data_to_insert = [
            (
                row['chat_row_id'],
                row['timestamp'],
                row['received_timestamp'],
                row['text_data'],
                row['from_me'],  # Convertido a booleano si es necesario
                row['number2'],
                row['status'],
                row['verified_name'],
                row['server'],
                row['device'],
                row['group'],
                row['description'],
                row['cliente'],
                row['estado'],
                row['municipio']
            ) for index, row in msg.iterrows()
        ]
        cursor.executemany(add_message, data_to_insert)
        mysql_con.commit()
except mysql.connector.Error as e:
    print(f"Error conectando a MySQL: {e}")
finally:
    mysql_con.close()

print("Tabla creada (si no existía) y datos subidos con éxito.")
