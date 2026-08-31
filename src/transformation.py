import pandas as pd

def transform_weather_data(df):
    df["time"] = pd.to_datetime(df["time"])
    return df