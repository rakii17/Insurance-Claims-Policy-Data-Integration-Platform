import argparse
import sqlite3
import pandas as pd
from pathlib import Path
import hashlib
import time

def validate_claims(df, conn):
    valid_rows = []
    rejected_rows = []

    # Get known policy IDs
    policies = [
    "POL001",
    "POL002",
    "POL003",
    "POL004",
    "POL005",
    "POL006",
    "POL007",
    "POL008",
    "POL009",
    "POL010",
    "POL011",
    "POL012",
    "POL013",
    "POL014",
    "POL015",
    "POL016",
    "POL017",
    "POL018",
    "POL019",
    "POL020",
    "POL021",
    "POL022",
    "POL023",
    "POL024",
    "POL025",
    "POL026",
    "POL027",
    "POL028",
    "POL029",
    "POL030"
    ]

    seen_claims = set()

    for _, row in df.iterrows():

        reason = None

        # Negative amount
        if row["settlement_amount"] < 0:
            reason = "NEGATIVE_SETTLEMENT_AMOUNT"

        # Invalid date
        elif pd.isna(
            pd.to_datetime(
                row["settlement_date"],
                errors="coerce"
            )
        ):
            reason = "INVALID_SETTLEMENT_DATE"

        # Unknown policy
        elif row["policy_id"] not in policies:
            reason = "UNKNOWN_POLICY_ID"

        # Duplicate claim within file
        elif row["claim_id"] in seen_claims:
            reason = "DUPLICATE_CLAIM_ID"

        if reason:
            rejected_rows.append({
                **row.to_dict(),
                "rejection_reason": reason
            })
        else:
            valid_rows.append(row.to_dict())

        seen_claims.add(row["claim_id"])

    return (
        pd.DataFrame(valid_rows),
        pd.DataFrame(rejected_rows)
    )

# Read command-line date
parser = argparse.ArgumentParser()
parser.add_argument("--date", required=True)

args = parser.parse_args()
start_time = time.time()

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

conn.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_run_log (
        run_date TEXT,
        status TEXT,
        rows_read INTEGER,
        rows_loaded INTEGER,
        rows_rejected INTEGER,
        start_time REAL,
        end_time REAL
    )
""")

conn.commit()

# Add delivery ID to raw data
df["delivery_id"] = delivery_id

# Validate incoming records
valid_df, rejected_df = validate_claims(df, conn)

print(f"Valid rows: {len(valid_df)}")
print(f"Rejected rows: {len(rejected_df)}")

if not rejected_df.empty:
    rejected_df.to_sql(
        "quarantine_claim_settlement",
        conn,
        if_exists="append",
        index=False
    )
    print("Rejected rows moved to quarantine.")

reject_rate = len(rejected_df) / len(df)

print(f"Reject rate: {reject_rate:.2%}")

if reject_rate > 0.20:
    end_time = time.time()

    conn.execute("""
        INSERT INTO pipeline_run_log
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        args.date,
        "FAILED",
        len(df),
        len(valid_df),
        len(rejected_df),
        start_time,
        end_time
    ))

    conn.commit()

    raise ValueError("Reject rate exceeds 20% threshold")

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

# Handle renamed columns
rename_map = {
    "status": "claim_status"
}

for old_name, new_name in rename_map.items():
    if old_name in incoming_columns and new_name not in incoming_columns:
        df.rename(columns={old_name: new_name}, inplace=True)

print(f"Columns after schema handling: {df.columns.tolist()}")

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
        # Remove old version of claims that are being restated
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
    
end_time = time.time()

conn.execute("""
    INSERT INTO pipeline_run_log
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
    args.date,
    "SUCCESS",
    len(df),
    len(valid_df),
    len(rejected_df),
    start_time,
    end_time
))

conn.commit()

# Check raw row count
raw_count = pd.read_sql(
    "SELECT COUNT(*) AS count FROM raw_claim_settlement",
    conn
).iloc[0]["count"]

print(f"Rows in raw table: {raw_count}")

# Close database connection
conn.close()