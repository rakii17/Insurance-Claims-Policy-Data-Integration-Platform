import pandas as pd
from src.load import get_db_connection, load_to_sqlite
from src.extract_csv import csv_data

customers_df = csv_data["customers"]

conn = get_db_connection()
load_to_sqlite(customers_df, "customers", conn)
conn.close()

conn = get_db_connection()
for table_name, df in csv_data.items():
    load_to_sqlite(df, table_name, conn)
conn.close()

conn = get_db_connection()
tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)
print(tables)
conn.close()

conn = get_db_connection()

tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)

for table in tables["name"]:
    count = pd.read_sql(
        f"SELECT COUNT(*) AS row_count FROM {table};",
        conn
    )
    print(f"{table}: {count.iloc[0]['row_count']} rows")

conn.close()