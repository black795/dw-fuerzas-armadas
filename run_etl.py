import pymssql

server = 'sql-ucb-sisger-ffaa-5756067.database.windows.net'
database = 'dw_ffaa'
username = 'alan'
password = 'S3cur3_P@ssw0rd_2026'

def execute_etl():
    try:
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        conn.autocommit(True)
        cursor = conn.cursor()
        
        print("Ejecutando ETL: Bronze a Silver...")
        cursor.execute("EXEC [silver].[sp_bronze_to_silver]")
        print("Capa Silver cargada exitosamente.")
        
        print("Ejecutando ETL: Generar Dimensión de Tiempo...")
        cursor.execute("EXEC [gold].[sp_generate_dim_tiempo]")
        print("Dimensión de Tiempo generada.")
        
        print("Ejecutando ETL: Silver a Gold...")
        cursor.execute("EXEC [gold].[sp_silver_to_gold]")
        print("Capa Gold cargada exitosamente.")
        
        print("¡Proceso ETL completado!")
        conn.close()
    except Exception as e:
        print(f"Error ejecutando ETL: {e}")

if __name__ == '__main__':
    execute_etl()
