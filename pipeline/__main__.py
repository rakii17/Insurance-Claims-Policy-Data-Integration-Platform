import argparse
import sqlite3
import pandas as pd
from pathlib import Path
import hashlib

# Read command-line date
parser = argparse.ArgumentParser()
parser.add_argument("--date", required=True)

args = parser.parse_args()

# Find input file
file_path = Path("data/landing") / f"partner_claims_{args.date}.csv"

df = pd.read_csv(file_path)

# Create delivery ID
file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
delivery_id = file_hash

print(f"Processing date: {args.date}")
print(f"Rows received: {len(df)}")

# Connect to SQLite
conn = sqlite3.connect("data/settlement.db")

# Add delivery ID to raw data
df["delivery_id"] = delivery_id

# Create raw table if needed
df.head(0).to_sql(
    "raw_claim_settlement",
    conn,
    if_exists="append",
    index=False
)

# Check for schema changes
existing_columns = pd.read_sql(
    "PRAGMA table_info(raw_claim_settlement)",
    conn
)["name"].tolist()

incoming_columns = df.columns.tolist()

new_columns = [
    column
    for column in incoming_columns
    if column not in existing_columns
]

if new_columns:
    print(f"Schema change detected. New columns: {new_columns}")

    for column in new_columns:
        conn.execute(
            f'ALTER TABLE raw_claim_settlement ADD COLUMN "{column}" TEXT'
        )

    conn.commit()

# Check duplicate delivery
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

    # Create status history table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dim_claim_status (
            claim_id TEXT,
            policy_id TEXT,
            settlement_date TEXT,
            settlement_amount REAL,
            claim_status TEXT,
            currency TEXT,
            valid_from TEXT,
            valid_to TEXT
        )
    """)

    conn.commit()

    # Read existing curated data
    try:
        existing_curated = pd.read_sql(
            "SELECT * FROM fact_claim_settlement",
            conn
        )

    except Exception:
        existing_curated = None

    # Prepare new data
    new_data = df.drop(
        columns=["delivery_id"]
    )
    
    # Load existing claim history
    history_df = pd.read_sql(
        "SELECT * FROM dim_claim_status",
        conn
    )

    # Current processing time/date
    valid_from = args.date
    
    # Check for existing versions of incoming claims
    for _, row in new_data.iterrows():

        existing_history = history_df[
            history_df["claim_id"] == row["claim_id"]
        ]

        if existing_history.empty:
            new_history = pd.DataFrame([{
                "claim_id": row["claim_id"],
                "policy_id": row["policy_id"],
                "settlement_date": row["settlement_date"],
                "settlement_amount": row["settlement_amount"],
                "claim_status": row["claim_status"],
                "currency": row["currency"],
                "valid_from": valid_from,
                "valid_to": None
            }])

            history_df = pd.concat(
                [history_df, new_history],
                ignore_index=True
            )

        else:
            history_df.loc[
                history_df["claim_id"] == row["claim_id"],
                "valid_to"
            ] = valid_from

            new_history = pd.DataFrame([{
                "claim_id": row["claim_id"],
                "policy_id": row["policy_id"],
                "settlement_date": row["settlement_date"],
                "settlement_amount": row["settlement_amount"],
                "claim_status": row["claim_status"],
                "currency": row["currency"],
                "valid_from": valid_from,
                "valid_to": None
            }])

            history_df = pd.concat(
                [history_df, new_history],
                ignore_index=True
            )

    history_df.to_sql(
        "dim_claim_status",
        conn,
        if_exists="replace",
        index=False
    )
    
    # Build curated table
    if existing_curated is None:
        curated_df = new_data

    else:
        # Remove old version of claims
        # that are being restated
        existing_curated = existing_curated[
            ~existing_curated["claim_id"].isin(
                new_data["claim_id"]
            )
        ]

        # Add latest versions
        curated_df = pd.concat(
            [
                existing_curated,
                new_data
            ],
            ignore_index=True
        )

    # Save curated data
    curated_df.to_sql(
        "fact_claim_settlement",
        conn,
        if_exists="replace",
        index=False
    )

    print(
        f"Rows in curated table: {len(curated_df)}"
    )

# Check raw row count
raw_count = pd.read_sql(
    "SELECT COUNT(*) AS count FROM raw_claim_settlement",
    conn
).iloc[0]["count"]

print(f"Rows in raw table: {raw_count}")

# Close database connection
conn.close()