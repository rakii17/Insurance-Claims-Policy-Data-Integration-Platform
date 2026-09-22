import sqlite3
from pathlib import Path

target_db_path = Path(__file__).resolve().parent.parent / "data" / "target.db"

def get_db_connection():
    conn = sqlite3.connect(target_db_path)
    return conn

def load_to_sqlite(df, table_name, conn):
    df.to_sql(table_name, conn, if_exists="replace", index=False)