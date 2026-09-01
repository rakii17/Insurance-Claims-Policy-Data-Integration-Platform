def validate_weather_data(df):
    if df.empty:
        raise ValueError("Weather DataFrame is empty")              
    
    expected_columns = ["time", "temperature_2m", "precipitation"] 
    missing_columns = set(expected_columns) - set(df.columns)     
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")
    
    null_counts = df.isnull().sum()
    if null_counts.any():
        raise ValueError(f"Missing values found: {null_counts[null_counts > 0]}")
    
    duplicate_count = df["time"].duplicated().sum()
    if duplicate_count > 0: 
        raise ValueError(f"Duplicate timestamps found: {duplicate_count}")
        
    if not df["temperature_2m"].between(-90, 60).all():
        raise ValueError("Invalid temperature values found")
    if (df["precipitation"] < 0).any():
        raise ValueError("Invalid precipitation values found")
    
    return True
    
def validate_dataframe(df, dataset_name, required_columns):
    if df.empty:
        raise ValueError(f"{dataset_name} DataFrame is empty")

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"{dataset_name} missing required columns: {missing_columns}"
        )

    null_counts = df[required_columns].isnull().sum()

    if null_counts.any():
        raise ValueError(
            f"{dataset_name} contains missing required values: "
            f"{null_counts[null_counts > 0].to_dict()}"
        )

    if df.duplicated().any():
        raise ValueError(f"{dataset_name} contains duplicate rows")

    return True