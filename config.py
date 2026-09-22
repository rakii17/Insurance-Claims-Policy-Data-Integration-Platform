from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_CSV_DIR = DATA_DIR / "raw" / "csv"
RAW_EXCEL_DIR = DATA_DIR / "raw" / "excel"
RAW_DATABASE_DIR = DATA_DIR / "raw" / "database"

SOURCE_DB_PATH = RAW_DATABASE_DIR / "source_system.db"
TARGET_DB_PATH = DATA_DIR / "target.db"