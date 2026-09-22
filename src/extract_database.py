import pandas as pd
import sqlite3
from config import TARGET_DB_PATH

def extract_database_data():

    conn = sqlite3.connect(TARGET_DB_PATH)

    policy_transactions_df = pd.read_sql("SELECT * FROM policy_transactions;", conn)
    premium_transactions_df = pd.read_sql("SELECT * FROM premium_transactions;", conn)
    claim_transactions_df = pd.read_sql("SELECT * FROM claim_transactions;", conn)
    
    conn.close()

    return {
        "policy_transactions": policy_transactions_df,
        "premium_transactions": premium_transactions_df,
        "claim_transactions": claim_transactions_df
    }