import pandas as pd
from src.load import get_db_connection, load_to_sqlite
from src.extract_csv import extract_csv_data
from src.extract_excel import extract_excel_data
from src.extract_database import extract_database_data
from src.extract_api import get_weather_data
from src.validation import (validate_weather_data, validate_dataframe, validate_data_types, validate_date_column, 
validate_policy_business_rules, validate_claim_business_rules, validate_payment_business_rules, validate_policy_transaction_business_rules,
validate_premium_transaction_business_rules, validate_claim_transaction_business_rules)
from src.transformation import (transform_claim_data, transform_payment_data, transform_policy_data, transform_customer_data)

#extract
csv_data = extract_csv_data()
excel_data = extract_excel_data()
database_data = extract_database_data()
weather_df = get_weather_data()

#required columns for validate
required_columns = {
    "agents": ["agent_id"],
    "claims": ["claim_id", "policy_id", "customer_id"],
    "customers": ["customer_id", "first_name", "last_name"],
    "payments": ["payment_id", "policy_id", "customer_id"],
    "policies": ["policy_id", "customer_id"],
    "branches": ["branch_id"],
    "policy_transactions": ["transaction_id", "policy_id"],
    "premium_transactions": ["payment_id", "policy_id"],
    "claim_transactions": ["claim_id", "policy_id"]
}

#businees keys
business_keys = {
    "agents": "agent_id",
    "claims": "claim_id",
    "customers": "customer_id",
    "payments": "payment_id",
    "policies": "policy_id",
    "branches": "branch_id",
    "policy_transactions": "transaction_id",
    "premium_transactions": "payment_id",
    "claim_transactions": "claim_id"
}

expected_types = {
    "agents": {
        "agent_id": pd.api.types.is_string_dtype,
        "agent_name": pd.api.types.is_string_dtype,
    },
    "claims": {
        "claim_id": pd.api.types.is_string_dtype,
        "claim_amount": pd.api.types.is_numeric_dtype,
    },
    "customers": {
        "customer_id": pd.api.types.is_string_dtype,
        "phone": pd.api.types.is_string_dtype,
    },
    "payments": {
        "payment_id": pd.api.types.is_string_dtype,
        "payment_amount": pd.api.types.is_numeric_dtype,
    },
    "policies": {
        "policy_id": pd.api.types.is_string_dtype,
        "premium_amount": pd.api.types.is_numeric_dtype,
        "sum_insured": pd.api.types.is_numeric_dtype,
    },
    "branches": {
        "branch_id": pd.api.types.is_string_dtype,
        "employee_count": pd.api.types.is_numeric_dtype,
    },
    "policy_transactions": {
        "transaction_id": pd.api.types.is_string_dtype,
    },
    "premium_transactions": {
        "payment_id": pd.api.types.is_string_dtype,
    },
    "claim_transactions": {
        "claim_id": pd.api.types.is_string_dtype,
    }
}

#combine
datasets = {}
datasets.update(csv_data)
datasets.update(excel_data)
datasets.update(database_data)
datasets["weather"] = weather_df
datasets["claims"] = transform_claim_data(datasets["claims"])
datasets["payments"] = transform_payment_data(datasets["payments"])
datasets["policies"] = transform_policy_data(datasets["policies"])
datasets["customers"] = transform_customer_data(datasets["customers"])
print("\n===== Transformed Customers Dtypes =====")
print(datasets["customers"].dtypes)
print("\n===== Policy Transactions =====")
print(datasets["policy_transactions"].columns)
print(datasets["policy_transactions"].head())

print("\n===== Premium Transactions =====")
print(datasets["premium_transactions"].columns)
print(datasets["premium_transactions"].head())

print("\n===== Claim Transactions =====")
print(datasets["claim_transactions"].columns)
print(datasets["claim_transactions"].head())

for table_name, df in datasets.items():
    if table_name == "weather":
        validate_weather_data(df)
        continue

    validate_dataframe(
        df,
        table_name,
        required_columns[table_name],
        business_keys[table_name]
    )
    validate_data_types(
        df,
        table_name,
        expected_types[table_name]
    )
    if table_name == "claims":
        validate_date_column(
            df,
            table_name,
            "claim_date"
        )
        validate_claim_business_rules(df)
        
    if table_name == "payments":
        validate_date_column(
            df,
            table_name,
            "payment_date"
        )
        validate_payment_business_rules(df)
        
    if table_name == "policies":
        validate_date_column(
            df,
            table_name,
            "policy_start_date"
        )

        validate_date_column(
            df,
            table_name,
            "policy_end_date"
        )
        validate_policy_business_rules(df)
        
    if table_name == "customers":
        validate_date_column(
            df,
            table_name,
            "date_of_birth"
        ) 
    if table_name == "branches":
        validate_date_column(
            df,
            table_name,
         "opening_date"
        )  
    if table_name == "policy_transactions":
        validate_policy_transaction_business_rules(df)

    if table_name == "premium_transactions":
        validate_premium_transaction_business_rules(df)

    if table_name == "claim_transactions":
        print("\n===== Invalid Claim Transactions =====")
        print(df[df["claim_amount"] <= 0])
        validate_claim_transaction_business_rules(df)

#load
conn = get_db_connection()
try:
    for table_name, df in datasets.items():
        load_to_sqlite(df, table_name, conn)

    conn.commit()

except Exception as e:
    conn.rollback()
    raise e

finally:
    conn.close()

#verify
conn = get_db_connection()
tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)
print("\n===== TABLES =====")
print(tables)

for table in tables["name"]:

    count = pd.read_sql(
        f"SELECT COUNT(*) AS row_count FROM {table};",
        conn
    )

    print(f"{table}: {count.iloc[0]['row_count']} rows")
conn.close()
