import pandas as pd
from pathlib import Path

raw_excel_path = Path("data/raw/excel")
excel_files = raw_excel_path.glob("*.xlsx")

excel_data = {}

for file in excel_files:
    df = pd.read_excel(file)
    excel_data[file.stem] = df

    print(f"\n===== {file.name} =====")
    print(df.head())
    print(df.shape)
    print(df.columns)
    print(df.dtypes)