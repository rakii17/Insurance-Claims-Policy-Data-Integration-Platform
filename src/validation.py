import pandas as pd

def validate_weather_data(df):
    if df.empty:
        raise ValueError("Weather DataFrame is empty")              
    
    expected_columns = ["time", "temperature_2m", "precipitation"] 
    missing_columns = set(expected_columns) - set(df.columns)     
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")
    
    null_counts = df.isnull().sum()
    if null_counts.any():
        raise ValueError(f"Missing values found: {null_counts[null_counts > 0]}")
    
    duplicate_count = df["time"].duplicated().sum()
    if duplicate_count > 0: 
        raise ValueError(f"Duplicate timestamps found: {duplicate_count}")
        
    if not df["temperature_2m"].between(-90, 60).all():
        raise ValueError("Invalid temperature values found")
    if (df["precipitation"] < 0).any():
        raise ValueError("Invalid precipitation values found")
    
    return True
    
def validate_dataframe(df, dataset_name, required_columns, business_key):

    if df.empty:
        raise ValueError(f"{dataset_name} DataFrame is empty")

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"{dataset_name} missing required columns: {missing_columns}"
        )

    null_counts = df[required_columns].isnull().sum()

    if null_counts.any():
        raise ValueError(
            f"{dataset_name} contains missing required values: "
            f"{null_counts[null_counts > 0].to_dict()}"
        )

    duplicate_keys = df[df[business_key].duplicated(keep=False)]

    if not duplicate_keys.empty:
        raise ValueError(
            f"{dataset_name} contains duplicate {business_key} values"
        )

    if df.duplicated().any():
        raise ValueError(f"{dataset_name} contains duplicate rows")

    return True

def validate_data_types(df, dataset_name, expected_types):
    for column, expected_type in expected_types.items():
        if column not in df.columns:
            continue

        if not expected_type(df[column]):
            raise ValueError(
                f"{dataset_name} column '{column}' has incorrect data type"
            )

    return True

def validate_date_column(df, dataset_name, column):
    if df[column].isnull().any():
        raise ValueError(
            f"{dataset_name} contains invalid dates in '{column}'"
        )

    if not pd.api.types.is_datetime64_any_dtype(df[column]):
        raise ValueError(
            f"{dataset_name} column '{column}' is not a datetime type"
        )

    return True

def validate_policy_business_rules(df):

    if (df["premium_amount"] <= 0).any():
        raise ValueError(
            "Policies contain invalid premium amounts"
        )

    if (df["sum_insured"] <= 0).any():
        raise ValueError(
            "Policies contain invalid sum insured values"
        )

    if (df["policy_end_date"] < df["policy_start_date"]).any():
        raise ValueError(
            "Policies contain end dates earlier than start dates"
        )

    return True

def validate_claim_business_rules(df):

    if (df["claim_amount"] <= 0).any():
        raise ValueError(
            "Claims contain invalid claim amounts"
        )

    return True

def validate_payment_business_rules(df):

    if (df["payment_amount"] <= 0).any():
        raise ValueError(
            "Payments contain invalid payment amounts"
        )

    return True

def validate_policy_transaction_business_rules(df):

    if (df["premium_amount"] <= 0).any():
        raise ValueError(
            "Policy transactions contain invalid premium amounts"
        )

    return True