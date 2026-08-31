def validate_weather_data(df):
    print(df.empty)                                                 #validate whether DataFrame is empty
    
    expected_columns = ["time", "temperature_2m", "precipitation"]  #validate for expected columns
    missing_columns = set(expected_columns) - set(df.columns)       #validate for missing columns
    print(missing_columns)
    
    print(df.isnull().sum())                                        #validate for missing values and total number of missing values
    
    print(df.duplicated().sum())                                    #validate for duplicate values
    
    print(df.dtypes)                                                #validate for datatypes
    
    print(df["temperature_2m"].min())                   
    print(df["temperature_2m"].max())
    print(df["precipitation"].min())
