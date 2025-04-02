import mysql.connector

def limpiar_registros_antiguos():
    MYSQL_USER = "admin"
    MYSQL_PASS = "S3gur1d4d2025"
    MYSQL_HOST = "158.69.26.160"
    MYSQL_DB = "data_wa"
    
    try:
        # Conectar a la base de datos
        con = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=MYSQL_DB
        )
        cursor = con.cursor()
        
        # Ver registros más recientes por cliente
        query_select = """
        WITH Ranked AS (
            SELECT 
                group_name, 
                total, 
                cliente, 
                fecha_subida,
                ROW_NUMBER() OVER (PARTITION BY cliente ORDER BY fecha_subida DESC) AS rn
            FROM total_participantes
        )
        SELECT group_name, total, cliente, fecha_subida
        FROM Ranked
        WHERE rn = 1;
        """
        cursor.execute(query_select)
        resultados = cursor.fetchall()
        print("Registros más recientes por cliente:")
        for row in resultados:
            print(row)
        
        # Desactivar el modo seguro
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")
        
        # Eliminar registros antiguos
        query_delete = """
        WITH Ranked AS (
            SELECT 
                id,
                ROW_NUMBER() OVER (PARTITION BY cliente ORDER BY fecha_subida DESC) AS rn
            FROM total_participantes
        )
        DELETE FROM total_participantes
        WHERE id IN (
            SELECT id FROM (SELECT id, rn FROM Ranked) AS sub WHERE rn > 1
        );
        """
        cursor.execute(query_delete)
        con.commit()
        print("Registros antiguos eliminados correctamente.")
        
        # Reactivar el modo seguro
        cursor.execute("SET SQL_SAFE_UPDATES = 1;")
        
    except mysql.connector.Error as e:
        print(f"Error en MySQL: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()

if __name__ == "__main__":
    limpiar_registros_antiguos()
