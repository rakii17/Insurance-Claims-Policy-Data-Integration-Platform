from src.extract_database import extract_database_data

first = extract_database_data()
second = extract_database_data()

print(first.keys())
print(second.keys())

for table in first:
    print(table, first[table].shape, second[table].shape)
    
    today = date.today().isoformat()
params = {
    "latitude": 12.9716,
    "longitude": 77.5946,
    "start_date": today,
    "end_date": today,
    "hourly": "temperature_2m,precipitation",
    "timezone": "Asia/Kolkata"
} 