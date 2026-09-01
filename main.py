import pandas as pd
from src.load import get_db_connection, load_to_sqlite
from src.extract_csv import csv_data
from src.extract_excel import excel_data
from src.extract_database import (policy_transactions_df, premium_transactions_df, claim_transactions_df)
from src.extract_api import df as weather_df

#csv connections
conn = get_db_connection()
for table_name, df in csv_data.items():
    load_to_sqlite(df, table_name, conn)
conn.close()

#target.db connections
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

#excel connections
branches_df = excel_data["branches"]

conn = get_db_connection()
load_to_sqlite(branches_df, "branches", conn)
conn.close()
print(branches_df.head())

conn = get_db_connection()
count = pd.read_sql(
    "SELECT COUNT(*) AS row_count FROM branches;",
    conn
)
print(f"branches: {count.iloc[0]['row_count']} rows")
conn.close()
print(branches_df.shape)

#source_system.db conenctions
conn = get_db_connection()
load_to_sqlite(
    policy_transactions_df,
    "policy_transactions",
    conn
)
load_to_sqlite(
    premium_transactions_df,
    "premium_transactions",
    conn
)
load_to_sqlite(
    claim_transactions_df,
    "claim_transactions",
    conn
)
conn.close()

#api connections
conn = get_db_connection()
load_to_sqlite(
    weather_df,
    "weather",
    conn
)
conn.close()