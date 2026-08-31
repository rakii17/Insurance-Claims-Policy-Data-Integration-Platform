import pandas as pd

agents_df = pd.read_csv("data/raw/csv/agents.csv")


print(agents_df.head())
print(agents_df.shape)
print(agents_df.columns)
print(agents_df.dtypes)
print(agents_df.isnull().sum())
print(agents_df.duplicated().sum())