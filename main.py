import pandas as pd
from src.load import get_db_connection, load_to_sqlite
from src.extract_csv import extract_csv_data
from src.extract_excel import extract_excel_data
from src.extract_database import extract_database_data
from src.extract_api import get_weather_data
from src.validation import validate_dataframe

#extract
csv_data = extract_csv_data()
excel_data = extract_excel_data()
database_data = extract_database_data()
weather_df = get_weather_data()

#required columns for validate
required_columns = {
    "agents": ["agent_id"],
    "claims": ["policy_id", "customer_id"],
    "customers": ["customer_id", "first_name", "last_name"],
    "payments": ["payment_id", "policy_id", "customer_id"],
    "policies": ["policy_id", "customer_id"],
    "branches": ["branch_id"],
    "policy_transactions": ["transaction_id", "policy_id"],
    "premium_transactions": ["payment_id", "policy_id"],
    "claim_transactions": ["claim_id", "policy_id"]
}

#combine
datasets = {}

datasets.update(csv_data)
datasets.update(excel_data)
datasets.update(database_data)
datasets["weather"] = weather_df

for table_name, df in datasets.items():

    if table_name == "weather":
        continue

    validate_dataframe(
        df,
        table_name,
        required_columns[table_name]
    )

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