import sqlite3
import pandas as pd
from datetime import datetime
import emoji
import mysql.connector
import os

config_file_path = 'config.txt'

# Función para obtener configuración
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

# Obtener configuración
config = get_or_prompt_config()

# Ubicaciones de la base de datos
msgstore_paths = ['/sdcard/msgstore.db', '/storage/emulated/0/WhatsApp/Databases/msgstore.db']
wa_db_paths = ['/sdcard/wa.db', '/storage/emulated/0/WhatsApp/Databases/wa.db']

# Función para conectar a la base de datos SQLite
def connect_to_db(paths):
    for path in paths:
        try:
            con = sqlite3.connect(path)
            print(f"Conectado a la base de datos en: {path}")
            return con
        except sqlite3.Error as e:
            print(f"Error conectando a {path}: {e}")
    print("No se pudo conectar a ninguna base de datos.")
    exit(1)

# Conectar a las bases de datos
con_msgstore = connect_to_db(msgstore_paths)
con_wa = connect_to_db(wa_db_paths)

# Leer datos de la base de datos msgstore.db
chv = pd.read_sql_query("SELECT * FROM chat_view", con_msgstore)
usuarios = pd.read_sql_query("SELECT * FROM jid", con_msgstore)
msg = pd.read_sql_query("SELECT * FROM message", con_msgstore)

# Leer datos de la base de datos wa.db
contacts = pd.read_sql_query("SELECT * FROM wa_contacts", con_wa)
contacts['jid'] = contacts['jid'].str.split('@').str[0]
descriptions = pd.read_sql_query("SELECT * FROM wa_group_descriptions", con_wa)
descriptions['jid'] = descriptions['jid'].str.split('@').str[0]
names = pd.read_sql_query("SELECT * FROM wa_vnames", con_wa)
names['jid'] = names['jid'].str.split('@').str[0]

# Obtener el número de participantes por grupo
group_members = pd.read_sql_query("SELECT gid, COUNT(*) AS total FROM wa_group_participants GROUP BY gid", con_wa)
group_members['gid'] = group_members['gid'].str.split('@').str[0]

# Procesamiento de datos
usuarios['user'] = usuarios['user'].astype(str).str[3:]
usuarios['server'] = usuarios['server'].apply(lambda x: 'celular' if x.endswith('.net') else ('grupo' if x.endswith('.us') else 'otro'))

msg = msg.loc[:, ['chat_row_id', 'timestamp', 'received_timestamp', 'text_data', 'from_me']].dropna(subset=['text_data'])
msg['timestamp'] = pd.to_datetime(msg['timestamp'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
msg['received_timestamp'] = pd.to_datetime(msg['received_timestamp'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')

# Funciones de mapeo
def mapping(df, column, id):
    return df.loc[df['_id'] == id, column].iloc[0] if id in df['_id'].values else None

msg['number2'] = msg['chat_row_id'].apply(lambda x: mapping(usuarios, 'user', x))
msg['server'] = msg['chat_row_id'].apply(lambda x: mapping(usuarios, 'server', x))
msg['device'] = msg['chat_row_id'].apply(lambda x: mapping(usuarios, 'device', x))
msg['group'] = msg['chat_row_id'].apply(lambda x: mapping(chv, 'subject', x))

msg = msg.merge(contacts[['jid', 'status']], left_on='number2', right_on='jid', how='left').drop(columns=['jid'])
msg = msg.merge(names[['jid', 'verified_name']], left_on='number2', right_on='jid', how='left').drop(columns=['jid'])
msg = msg.merge(descriptions[['jid', 'description']], left_on='number2', right_on='jid', how='left').drop(columns=['jid'])

# Eliminar emojis
def remove_emojis(text):
    return emoji.replace_emoji(text, replace='') if text else text

msg['text_data'] = msg['text_data'].apply(remove_emojis)
msg['description'] = msg['description'].apply(remove_emojis)
msg['group'] = msg['group'].apply(remove_emojis)

# Agregar datos de configuración
msg['cliente'] = config['cliente']
msg['estado'] = config['estado']
msg['municipio'] = config['municipio']

# Guardar datos en CSV
csv_file_path = 'messages_processed.csv'
msg.to_csv(csv_file_path, index=False)

# Conexión MySQL
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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS total_participantes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            group_name VARCHAR(255),
            total INT,
            UNIQUE KEY unique_group (group_name)
        )
        """)
        
        add_participants = """
        INSERT INTO total_participantes (group_name, total) 
        VALUES (%s, %s) 
        ON DUPLICATE KEY UPDATE total = VALUES(total);
        """
        
        participant_data = [tuple(row) for row in group_members[['gid', 'total']].itertuples(index=False)]
        cursor.executemany(add_participants, participant_data)
        mysql_con.commit()
except mysql.connector.Error as e:
    print(f"Error en MySQL: {e}")
finally:
    mysql_con.close()

print("Datos subidos con éxito.")
