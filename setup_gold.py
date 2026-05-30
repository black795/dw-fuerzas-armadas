import pymssql

server = 'sql-ucb-sisger-ffaa-5756067.database.windows.net'
database = 'dw_ffaa'
username = 'alan'
password = '4-v3ry-53cr37-p455w0rd'
sql_file = r'c:\Users\Windows 11 Pro\Downloads\evaluacion3\Modelos\gold_schema.sql.txt'

def execute_script():
    try:
        print(f"Connecting to {server}...")
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        conn.autocommit(True)
        cursor = conn.cursor()
        
        with open(sql_file, 'r', encoding='utf-8') as file:
            sql_script = file.read()
            
        # Split script by GO
        commands = sql_script.split('GO')
        
        for command in commands:
            cmd = command.strip()
            if cmd:
                print(f"Executing: {cmd[:50]}...")
                cursor.execute(cmd)
                
        print("Schema created successfully!")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    execute_script()
