import sqlite3
import pandas as pd

source_db_path = "data/raw/database/source_system.db"

conn = sqlite3.connect(source_db_path)

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
).fetchall()

policy_transactions_df = pd.read_sql(
    "SELECT * FROM policy_transactions;",
    conn
)
premium_transactions_df = pd.read_sql(
    "SELECT * FROM premium_transactions;",
    conn
)
claim_transactions_df = pd.read_sql(
    "SELECT * FROM claim_transactions;",
    conn
)
print("Policy transactions:", policy_transactions_df.shape)
print("Premium transactions:", premium_transactions_df.shape)
print("Claim transactions:", claim_transactions_df.shape)
conn.close()