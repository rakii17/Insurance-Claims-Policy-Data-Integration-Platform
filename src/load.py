import sqlite3

def get_db_connection():
    conn = sqlite3.connect("data/target.db")
    return conn

def load_to_sqlite(df, table_name, conn):
    df.to_sql(table_name, conn, if_exists="replace", index=False)