import sqlite3
import pandas as pd

source_db_path = "data/raw/database/source_system.db"

def extract_database_data():

    conn = sqlite3.connect(source_db_path)

    policy_transactions_df = pd.read_sql("SELECT * FROM policy_transactions;", conn)
    premium_transactions_df = pd.read_sql("SELECT * FROM premium_transactions;", conn)
    claim_transactions_df = pd.read_sql("SELECT * FROM claim_transactions;", conn)
    
    conn.close()

    return {
        "policy_transactions": policy_transactions_df,
        "premium_transactions": premium_transactions_df,
        "claim_transactions": claim_transactions_df
    }