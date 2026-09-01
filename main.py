import pandas as pd
from src.load import get_db_connection, load_to_sqlite

conn = get_db_connection()

tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)

print(tables)

conn.close()