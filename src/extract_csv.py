import pandas as pd
from pathlib import Path

raw_csv_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "csv"

def extract_csv_data():
    csv_data = {}
    csv_files = raw_csv_path.glob("*.csv")

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