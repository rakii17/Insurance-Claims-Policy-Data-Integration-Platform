import argparse
import sqlite3
import pandas as pd
from pathlib import Path
import hashlib

parser = argparse.ArgumentParser()
parser.add_argument("--date", required=True)

args = parser.parse_args()

file_path = Path("data/landing") / f"partner_claims_{args.date}.csv"

df = pd.read_csv(file_path)
file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
delivery_id = file_hash

print(f"Processing date: {args.date}")
print(f"Rows received: {len(df)}")


# Create database
conn = sqlite3.connect("data/settlement.db")

df["delivery_id"] = delivery_id

df.head(0).to_sql(
    "raw_claim_settlement",
    conn,
    if_exists="append",
    index=False
)

# Check if delivery already exists
existing_delivery = pd.read_sql(
    "SELECT COUNT(*) AS count FROM raw_claim_settlement WHERE delivery_id = ?",
    conn,
    params=(delivery_id,)
).iloc[0]["count"]

if existing_delivery > 0:
    print("Delivery already processed. Skipping load.")
else:
    # Load raw records
    df.to_sql(
        "raw_claim_settlement",
        conn,
        if_exists="append",
        index=False
    )

    print("New delivery loaded.")
    
    curated_df = df.drop(columns=["delivery_id"])

    curated_df.to_sql(
        "fact_claim_settlement",
        conn,
        if_exists="replace",
        index=False
    )

    print(f"Rows in curated table: {len(curated_df)}")
    
raw_count = pd.read_sql(
    "SELECT COUNT(*) AS count FROM raw_claim_settlement",
    conn
).iloc[0]["count"]

print(f"Rows in raw table: {raw_count}")

conn.close()