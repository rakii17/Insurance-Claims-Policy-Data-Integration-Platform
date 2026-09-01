import pandas as pd
from src.load import get_db_connection, load_to_sqlite
from src.extract_csv import extract_csv_data
from src.extract_excel import extract_excel_data
from src.extract_database import extract_database_data
from src.extract_api import get_weather_data

#extract
csv_data = extract_csv_data()
excel_data = extract_excel_data()
database_data = extract_database_data()
weather_df = get_weather_data()

#combine
datasets = {}

datasets.update(csv_data)
datasets.update(excel_data)
datasets.update(database_data)
datasets["weather"] = weather_df

#load
conn = get_db_connection()
for table_name, df in datasets.items():
    load_to_sqlite(df, table_name, conn)
conn.close()

#verify
conn = get_db_connection()
tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)
print("\n===== TABLES =====")
print(tables)

for table in tables["name"]:

    count = pd.read_sql(
        f"SELECT COUNT(*) AS row_count FROM {table};",
        conn
    )

    print(f"{table}: {count.iloc[0]['row_count']} rows")
conn.close()