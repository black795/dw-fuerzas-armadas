import pymssql
import pandas as pd
import os

# Connection Configuration
server = 'server02-fuerzas-armadas-bolivia.database.windows.net'
database = 'erp-fuerzas-armadas-bolivia-2'
username = 'userSisGer'
password = 'C0ntr4s3n!a'

tables = [
    "tbl_operaciones",
    "tbl_zonas",
    "tbl_tipos_operacion",
    "tbl_movimientos_personal",
    "tbl_efectivos",
    "tbl_especialidades",
    "tbl_rangos",
    "tbl_tipos_movimiento",
    "tbl_unidades",
    "tbl_estructura_organizacional"
]

output_dir = 'Dataset'
os.makedirs(output_dir, exist_ok=True)

print(f"Connecting to database {database} at {server}...")
try:
    conn = pymssql.connect(server=server, user=username, password=password, database=database)
    print("Connection successful!")
    
    # Query all tables in the database
    query_tables = "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
    cursor = conn.cursor()
    cursor.execute(query_tables)
    db_tables = cursor.fetchall()
    
    print(f"Found {len(db_tables)} tables in the database.")
    for schema, table_name in db_tables:
        full_table_name = f"[{schema}].[{table_name}]"
        print(f"Extracting {full_table_name}...")
        query = f"SELECT * FROM {full_table_name}"
        try:
            df = pd.read_sql(query, conn)
            output_path = os.path.join(output_dir, f"{schema}_{table_name}.csv")
            df.to_csv(output_path, index=False)
            print(f"  -> Saved {len(df)} rows to {output_path}")
        except Exception as e:
            print(f"  -> Error extracting {full_table_name}: {e}")
            
    conn.close()
    print("Extraction complete!")
except Exception as e:
    print(f"Failed to connect to database: {e}")
