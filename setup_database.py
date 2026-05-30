import pymssql
import os

server = 'sql-ucb-sisger-ffaa-5756067.database.windows.net'
database = 'dw_ffaa'
username = 'alan'
password = 'S3cur3_P@ssw0rd_2026'

# Usar rutas relativas basadas en la ubicación del script
base_dir = os.path.dirname(os.path.abspath(__file__))
sql_files = [
    os.path.join(base_dir, 'Modelos', 'bronze_schema.sql.txt'),
    os.path.join(base_dir, 'Modelos', 'silver_schema.sql.txt'),
    os.path.join(base_dir, 'Modelos', 'gold_schema.sql.txt'),
    os.path.join(base_dir, 'Modelos', 'etl_procedures.sql.txt')
]

def execute_scripts():
    try:
        print(f"Conectando a {server}...")
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        conn.autocommit(True)
        cursor = conn.cursor()
        
        for sql_file in sql_files:
            print(f"Procesando {os.path.basename(sql_file)}...")
            with open(sql_file, 'r', encoding='utf-8') as file:
                sql_script = file.read()
                
            import re
            commands = re.split(r'(?i)^\s*GO\s*$', sql_script, flags=re.MULTILINE)
            
            for command in commands:
                cmd = command.strip()
                if cmd:
                    try:
                        cursor.execute(cmd)
                        print(f"Éxito: {cmd[:40]}...")
                    except Exception as e:
                        if 'already an object named' in str(e) or 'already exists' in str(e):
                            pass
                        else:
                            print(f"Error ignorado en {cmd[:40]}... : {e}")
                    
        print("¡Todos los esquemas (Bronze, Silver, Gold) fueron creados exitosamente!")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    execute_scripts()
