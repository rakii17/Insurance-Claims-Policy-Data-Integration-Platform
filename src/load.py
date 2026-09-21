import sqlite3

def get_db_connection():
    conn = sqlite3.connect("data/target.db")
    return conn

def load_to_sqlite(df, table_name, conn):
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e