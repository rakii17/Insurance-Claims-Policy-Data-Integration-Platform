import pandas as pd

def transform_weather_data(df):
    df["time"] = pd.to_datetime(df["time"])
    return df

def transform_claim_data(df):
    df = df.copy()

    df["claim_date"] = pd.to_datetime(
        df["claim_date"],
        errors="coerce"
    )

    return df

def transform_payment_data(df):
    df = df.copy()

    df["payment_date"] = pd.to_datetime(
        df["payment_date"],
        errors="coerce"
    )

    return df

def transform_policy_data(df):
    df = df.copy()

    df["policy_start_date"] = pd.to_datetime(
        df["policy_start_date"],
        errors="coerce"
    )

    df["policy_end_date"] = pd.to_datetime(
        df["policy_end_date"],
        errors="coerce"
    )

    return df

def transform_customer_data(df):
    df = df.copy()

    df["date_of_birth"] = pd.to_datetime(
        df["date_of_birth"],
        errors="coerce"
    )

    return df