import pymssql
import pandas as pd
import os
import math

server = 'sql-ucb-sisger-ffaa-5756067.database.windows.net'
database = 'dw_ffaa'
username = 'alan'
password = 'S3cur3_P@ssw0rd_2026'

base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.join(base_dir, 'Dataset')

# Mapeo de CSVs a tablas bronze
tables_mapping = {
    'oltp_tbl_zonas.csv': 'bronze.zonas_raw',
    'oltp_tbl_tipos_operacion.csv': 'bronze.tipos_operacion_raw',
    'oltp_tbl_especialidades.csv': 'bronze.especialidades_raw',
    'oltp_tbl_rangos.csv': 'bronze.rangos_raw',
    'oltp_tbl_tipos_movimiento.csv': 'bronze.tipos_movimiento_raw',
    'oltp_tbl_unidades.csv': 'bronze.unidades_raw',
    'oltp_tbl_estructura_organizacional.csv': 'bronze.estructura_organizacional_raw',
    'oltp_tbl_efectivos.csv': 'bronze.efectivos_raw',
    'oltp_tbl_movimientos_personal.csv': 'bronze.movimientos_personal_raw',
    'oltp_tbl_operaciones.csv': 'bronze.operaciones_raw'
}

def clean_value(val):
    if pd.isna(val) or val is None:
        return None
    return str(val)

def load_data():
    try:
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        cursor = conn.cursor()
        
        for csv_file, table_name in tables_mapping.items():
            file_path = os.path.join(dataset_dir, csv_file)
            if not os.path.exists(file_path):
                print(f"File {csv_file} no encontrado, omitiendo...")
                continue
                
            print(f"Cargando {csv_file} a {table_name}...")
            df = pd.read_csv(file_path)
            
            # Crear la instrucción INSERT
            cols = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
            
            # Eliminar datos anteriores
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            
            # Preparar e insertar datos
            records = []
            for _, row in df.iterrows():
                cleaned_row = tuple(clean_value(val) for val in row)
                records.append(cleaned_row)
            
            if records:
                cursor.executemany(insert_query, records)
                conn.commit()
                print(f"{len(records)} filas insertadas.")
                
        print("Carga Bronze completa.")
        conn.close()
    except Exception as e:
        print(f"Error cargando datos: {e}")

if __name__ == '__main__':
    load_data()
