import mysql.connector

# Configuración de la conexión
conn = mysql.connector.connect(
    host='158.69.26.160',
    user='admin',
    password='F@c3b00k',
    database='data_wa'
)

cursor = conn.cursor()

try:
    print("🔄 Iniciando eliminación de duplicados...")

    # Desactivar el modo seguro
    cursor.execute("SET SQL_SAFE_UPDATES = 0;")

    # Eliminar duplicados
    delete_query = """
    DELETE FROM extraccion4
    WHERE id IN (
        SELECT id FROM (
            SELECT id, 
                   ROW_NUMBER() OVER (PARTITION BY text_data, received_timestamp ORDER BY id) AS fila
            FROM extraccion4
        ) AS subquery
        WHERE fila > 1
    );
    """
    cursor.execute(delete_query)

    # Reactivar el modo seguro
    cursor.execute("SET SQL_SAFE_UPDATES = 1;")

    # Confirmar cambios
    conn.commit()

    print("✅ Eliminación de duplicados completada con éxito.")

except Exception as e:
    print(f"❌ Error durante la eliminación de duplicados: {e}")

finally:
    # Cerrar conexión
    cursor.close()
    conn.close()
    print("🔒 Conexión cerrada.")
