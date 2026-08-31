import pandas as pd
from pathlib import Path

raw_csv_path = Path("data/raw/csv")
csv_files = raw_csv_path.glob("*.csv")

csv_data = {}

for file in csv_files:
    df = pd.read_csv(file)
    csv_data[file.stem] = df
    
    print(f"\n===== {file.name} =====")
    print(df.head())
    print(df.shape)
    print(df.columns)
    print(df.dtypes)
    print(df.isnull().sum())
    print(df.duplicated().sum())
    
print(csv_data.keys()) 

