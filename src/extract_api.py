import requests
import pandas as pd
from .validation import validate_weather_data
from .transformation import transform_weather_data
from config import (API_URL,WEATHER_LATITUDE,WEATHER_LONGITUDE,WEATHER_TIMEZONE,WEATHER_HOURLY_FIELDS)

def extract_api_data(api_url, params):
    response = requests.get(api_url, params=params, timeout=30) #sending GET request and storing API response
    response.raise_for_status()                                 #throws HTTP error when occurs
    api_data = response.json()                                  #converts API response into Python object
    return api_data["hourly"]

def get_weather_data(process_data):
    params = {
        "latitude": WEATHER_LATITUDE,
        "longitude": WEATHER_LONGITUDE,
        "start_date": process_data,
        "end_date": process_data,
        "hourly": WEATHER_HOURLY_FIELDS,
        "timezone": WEATHER_TIMEZONE
    }

    weather_data = extract_api_data(API_URL, params)
    df = pd.DataFrame(weather_data)
    print(df.columns)

    validate_weather_data(df)
    df = transform_weather_data(df)
    print(df.dtypes)

    return df