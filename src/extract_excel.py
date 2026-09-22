import pandas as pd
from config import RAW_EXCEL_DIR   
    
def extract_excel_data():
    excel_data = {}
    excel_files = RAW_EXCEL_DIR.glob("*.xlsx")

    for file in excel_files:
        df = pd.read_excel(file)
        excel_data[file.stem] = df

        print(f"\n===== {file.name} =====")
        print(df.head())
        print(df.shape)
        print(df.columns)
        print(df.dtypes)
    
    return excel_data