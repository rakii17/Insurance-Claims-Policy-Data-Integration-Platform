import requests
import pandas as pd
from .validation import validate_weather_data
from .transformation import transform_weather_data

api_url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 12.9716,
    "longitude": 77.5946,
    "start_date": "2026-08-30",
    "end_date": "2026-08-30",
    "hourly": "temperature_2m,precipitation",
    "timezone": "Asia/Kolkata"
} 

def extract_api_data(api_url, params):
    response = requests.get(api_url, params=params) #sending GET request and storing API response
    response.raise_for_status()                     #throws HTTP error when occurs
    api_data = response.json()                      #converts API response into Python object
    return api_data["hourly"]

def get_weather_data():

    weather_data = extract_api_data(api_url, params)
    df = pd.DataFrame(weather_data)
    print(df.columns)

    validate_weather_data(df)
    df = transform_weather_data(df)
    print(df.dtypes)

    return df