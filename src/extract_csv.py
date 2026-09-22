import pandas as pd
from config import RAW_CSV_DIR

def extract_csv_data():
    csv_data = {}
    csv_files = RAW_CSV_DIR.glob("*.csv")

    for file in csv_files:
        df = pd.read_csv(file, dtype={"phone": "string"})
        csv_data[file.stem] = df
        
        print(f"\n===== {file.name} =====")
        print(df.head())
        print(df.shape)
        print(df.columns)
        print(df.dtypes)
        print(df.isnull().sum())
        print(df.duplicated().sum())

    return csv_data