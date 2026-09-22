from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_CSV_DIR = DATA_DIR / "raw" / "csv"
RAW_EXCEL_DIR = DATA_DIR / "raw" / "excel"
RAW_DATABASE_DIR = DATA_DIR / "raw" / "database"

SOURCE_DB_PATH = RAW_DATABASE_DIR / "source_system.db"
TARGET_DB_PATH = DATA_DIR / "target.db"

API_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_LATITUDE = 12.9716
WEATHER_LONGITUDE = 77.5946
WEATHER_TIMEZONE = "Asia/Kolkata"
WEATHER_HOURLY_FIELDS = "temperature_2m,precipitation"