import requests
import pandas as pd

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

weather_data = extract_api_data(api_url, params)    #store returned JSON object into weather_data
df = pd.DataFrame(weather_data)                     #convert JSON into Dataframe(rows&columns)
# print(df.to_string(index=False))                    #convert to string and not printing index row numbers
print(df)