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