import pandas as pd
from src.load import get_db_connection, load_to_sqlite
from src.extract_csv import extract_csv_data
from src.extract_excel import extract_excel_data
from src.extract_database import extract_database_data
from src.extract_api import get_weather_data
from src.validation import (validate_weather_data, validate_dataframe, validate_data_types, validate_date_column, 
validate_policy_business_rules, validate_claim_business_rules, validate_payment_business_rules, validate_policy_transaction_business_rules,
validate_premium_transaction_business_rules, validate_claim_transaction_business_rules)
from src.transformation import (transform_claim_data, transform_payment_data, transform_policy_data, transform_customer_data)
from src.logger import logger

def run_pipeline(process_data):
    logger.info("ETL Pipeline Started")

    process_data = "2026-09-21"

    #extract
    csv_data = extract_csv_data()
    excel_data = extract_excel_data()
    database_data = extract_database_data()
    weather_df = get_weather_data(process_data)

    logger.info("Data extraction completed successfully")

    #required columns for validate
    required_columns = {
        "agents": ["agent_id"],
        "claims": ["claim_id", "policy_id", "customer_id"],
        "customers": ["customer_id", "first_name", "last_name"],
        "payments": ["payment_id", "policy_id", "customer_id"],
        "policies": ["policy_id", "customer_id"],
        "branches": ["branch_id"],
        "policy_transactions": ["transaction_id", "policy_id"],
        "premium_transactions": ["payment_id", "policy_id"],
        "claim_transactions": ["claim_id", "policy_id"]
    }

    #businees keys
    business_keys = {
        "agents": "agent_id",
        "claims": "claim_id",
        "customers": "customer_id",
        "payments": "payment_id",
        "policies": "policy_id",
        "branches": "branch_id",
        "policy_transactions": "transaction_id",
        "premium_transactions": "payment_id",
        "claim_transactions": "claim_id"
    }

    expected_types = {
        "agents": {
            "agent_id": pd.api.types.is_string_dtype,
            "agent_name": pd.api.types.is_string_dtype,
        },
        "claims": {
            "claim_id": pd.api.types.is_string_dtype,
            "claim_amount": pd.api.types.is_numeric_dtype,
        },
        "customers": {
            "customer_id": pd.api.types.is_string_dtype,
            "phone": pd.api.types.is_string_dtype,
        },
        "payments": {
            "payment_id": pd.api.types.is_string_dtype,
            "payment_amount": pd.api.types.is_numeric_dtype,
        },
        "policies": {
            "policy_id": pd.api.types.is_string_dtype,
            "premium_amount": pd.api.types.is_numeric_dtype,
            "sum_insured": pd.api.types.is_numeric_dtype,
        },
        "branches": {
            "branch_id": pd.api.types.is_string_dtype,
            "employee_count": pd.api.types.is_numeric_dtype,
        },
        "policy_transactions": {
            "transaction_id": pd.api.types.is_string_dtype,
        },
        "premium_transactions": {
            "payment_id": pd.api.types.is_string_dtype,
        },
        "claim_transactions": {
            "claim_id": pd.api.types.is_string_dtype,
        }
    }

    #combine
    datasets = {}
    datasets.update(csv_data)
    datasets.update(excel_data)
    datasets.update(database_data)
    datasets["weather"] = weather_df
    datasets["claims"] = transform_claim_data(datasets["claims"])
    datasets["payments"] = transform_payment_data(datasets["payments"])
    datasets["policies"] = transform_policy_data(datasets["policies"])
    datasets["customers"] = transform_customer_data(datasets["customers"])

    print("\n===== Transformed Customers Dtypes =====")
    print(datasets["customers"].dtypes)
    print("\n===== Policy Transactions =====")
    print(datasets["policy_transactions"].columns)
    print(datasets["policy_transactions"].head())

    print("\n===== Premium Transactions =====")
    print(datasets["premium_transactions"].columns)
    print(datasets["premium_transactions"].head())

    print("\n===== Claim Transactions =====")
    print(datasets["claim_transactions"].columns)
    print(datasets["claim_transactions"].head())

    logger.info("Data transformation completed successfully")

    for table_name, df in datasets.items():
        if table_name == "weather":
            validate_weather_data(df)
            continue

        validate_dataframe(
            df,
            table_name,
            required_columns[table_name],
            business_keys[table_name]
        )
        validate_data_types(
            df,
            table_name,
            expected_types[table_name]
        )
        if table_name == "claims":
            validate_date_column(
                df,
                table_name,
                "claim_date"
            )
            validate_claim_business_rules(df)
        
        if table_name == "payments":
            validate_date_column(
                df,
                table_name,
               "payment_date"
            )
            validate_payment_business_rules(df)
        
        if table_name == "policies":
            validate_date_column(
                df,
                table_name,
                "policy_start_date"
            )

            validate_date_column(
                df,
                table_name,
                "policy_end_date"
            )
            validate_policy_business_rules(df)
        
        if table_name == "customers":
            validate_date_column(
                df,
                table_name,
                "date_of_birth"
            ) 
        if table_name == "branches":
            validate_date_column(
                df,
                table_name,
             "opening_date"
           )  
        if table_name == "policy_transactions":
            validate_policy_transaction_business_rules(df)
    
        if table_name == "premium_transactions":
            validate_premium_transaction_business_rules(df)

        if table_name == "claim_transactions":
            validate_claim_transaction_business_rules(df)

    logger.info("Data validation completed successfully")

    #load
    conn = get_db_connection()
    try:
        for table_name, df in datasets.items():
           load_to_sqlite(df, table_name, conn)

        conn.commit()

    except Exception as e:
        conn.rollback()
        logger.error(f"ETL Pipeline failed during load: {e}")
        raise e

    finally:
        conn.close()

    logger.info("Data loaded into SQLite successfully")
    logger.info("ETL Pipeline Completed Successfully")

    #verify
    conn = get_db_connection()
    tables = pd.read_sql(
     "SELECT name FROM sqlite_master WHERE type='table';",
        conn
    )
    print("\n===== TABLES =====")
    print(tables)

    for table in tables["name"]:

       count = pd.read_sql(
           f"SELECT COUNT(*) AS row_count FROM {table};",
           conn
        )

    print(f"{table}: {count.iloc[0]['row_count']} rows")
    conn.close()
    
if __name__ == "__main__":
    run_pipeline("2026-09-21")

# Output:
# [Running] python -u "c:\Users\Administrator\Documents\GitHub\Insurance Claims & Policy Data Integration Platform\main.py"

# ===== agents.csv =====
#   agent_id      agent_name           branch       city        state agent_type
# 0    AG001     Manoj Gupta          Andheri     Mumbai  Maharashtra   Employee
# 1    AG002       Rina Shah        Satellite  Ahmedabad      Gujarat    Partner
# 2    AG003      Deepak Rao       Whitefield  Bengaluru    Karnataka   Employee
# 3    AG004  Pooja Malhotra  Connaught Place      Delhi        Delhi    Partner
# 4    AG005     Kiran Reddy    Banjara Hills  Hyderabad    Telangana   Employee
# (8, 6)
# Index(['agent_id', 'agent_name', 'branch', 'city', 'state', 'agent_type'], dtype='str')
# agent_id      str
# agent_name    str
# branch        str
# city          str
# state         str
# agent_type    str
# dtype: object
# agent_id      0
# agent_name    0
# branch        0
# city          0
# state         0
# agent_type    0
# dtype: int64
# 0

# ===== claims.csv =====
#   claim_id policy_id customer_id  ... claim_type claim_amount  claim_status
# 0   CLM001    POL001     CUST001  ...    Medical        75000      Approved
# 1   CLM002    POL002     CUST002  ...    Vehicle        45000       Pending
# 2   CLM003    POL003     CUST003  ...   Property       120000      Approved

# [3 rows x 7 columns]
# (3, 7)
# Index(['claim_id', 'policy_id', 'customer_id', 'claim_date', 'claim_type',
#        'claim_amount', 'claim_status'],
#       dtype='str')
# claim_id          str
# policy_id         str
# customer_id       str
# claim_date        str
# claim_type        str
# claim_amount    int64
# claim_status      str
# dtype: object
# claim_id        0
# policy_id       0
# customer_id     0
# claim_date      0
# claim_type      0
# claim_amount    0
# claim_status    0
# dtype: int64
# 0

# ===== customers.csv =====
#   customer_id first_name  ...                    email       phone
# 0     CUST001     Rajesh  ...  rajesh.sharma@email.com  9876543210
# 1     CUST002      Priya  ...    priya.patel@email.com  9876543211
# 2     CUST003       Amit  ...     amit.kumar@email.com  9876543212
# 3     CUST004       Neha  ...     neha.verma@email.com  9876543213
# 4     CUST005      Arjun  ...    arjun.reddy@email.com  9876543214

# [5 rows x 9 columns]
# (12, 9)
# Index(['customer_id', 'first_name', 'last_name', 'date_of_birth', 'gender',
#        'city', 'state', 'email', 'phone'],
#       dtype='str')
# customer_id         str
# first_name          str
# last_name           str
# date_of_birth       str
# gender              str
# city                str
# state               str
# email               str
# phone            string
# dtype: object
# customer_id      0
# first_name       0
# last_name        0
# date_of_birth    0
# gender           0
# city             0
# state            0
# email            0
# phone            0
# dtype: int64
# 0

# ===== payments.csv =====
#   payment_id policy_id  ... payment_method payment_status
# 0     PAY001    POL001  ...            UPI     Successful
# 1     PAY002    POL002  ...    Credit Card     Successful
# 2     PAY003    POL003  ...    Net Banking     Successful
# 3     PAY004    POL004  ...            UPI     Successful
# 4     PAY005    POL005  ...     Debit Card     Successful

# [5 rows x 7 columns]
# (12, 7)
# Index(['payment_id', 'policy_id', 'customer_id', 'payment_date',
#        'payment_amount', 'payment_method', 'payment_status'],
#       dtype='str')
# payment_id          str
# policy_id           str
# customer_id         str
# payment_date        str
# payment_amount    int64
# payment_method      str
# payment_status      str
# dtype: object
# payment_id        0
# policy_id         0
# customer_id       0
# payment_date      0
# payment_amount    0
# payment_method    0
# payment_status    0
# dtype: int64
# 0

# ===== policies.csv =====
#   policy_id customer_id policy_type  ... premium_amount sum_insured  policy_status
# 0    POL001     CUST001      Health  ...          18500      500000         Active
# 1    POL002     CUST002       Motor  ...          12400      350000         Active
# 2    POL003     CUST003      Health  ...          22000      750000        Expired
# 3    POL004     CUST004        Life  ...          32000     2500000         Active
# 4    POL005     CUST005       Motor  ...          15600      600000         Active

# [5 rows x 8 columns]
# (12, 8)
# Index(['policy_id', 'customer_id', 'policy_type', 'policy_start_date',
#        'policy_end_date', 'premium_amount', 'sum_insured', 'policy_status'],
#       dtype='str')
# policy_id              str
# customer_id            str
# policy_type            str
# policy_start_date      str
# policy_end_date        str
# premium_amount       int64
# sum_insured          int64
# policy_status          str
# dtype: object
# policy_id            0
# customer_id          0
# policy_type          0
# policy_start_date    0
# policy_end_date      0
# premium_amount       0
# sum_insured          0
# policy_status        0
# dtype: int64
# 0

# ===== branches.xlsx =====
#   branch_id     branch_name  ... employee_count branch_status
# 0     BR001  Mumbai Central  ...             42        Active
# 1     BR002    Andheri West  ...             28        Active
# 2     BR003          Bandra  ...             31        Active
# 3     BR004           Thane  ...             25        Active
# 4     BR005     Navi Mumbai  ...             23        Active

# [5 rows x 10 columns]
# (100, 10)
# Index(['branch_id', 'branch_name', 'city', 'state', 'region', 'branch_type',
#        'manager_name', 'opening_date', 'employee_count', 'branch_status'],
#       dtype='str')
# branch_id                    str
# branch_name                  str
# city                         str
# state                        str
# region                       str
# branch_type                  str
# manager_name                 str
# opening_date      datetime64[us]
# employee_count             int64
# branch_status                str
# dtype: object
# Index(['time', 'temperature_2m', 'precipitation'], dtype='str')
# time              datetime64[us]
# temperature_2m           float64
# precipitation            float64
# dtype: object

# ===== Transformed Customers Dtypes =====
# customer_id                 str
# first_name                  str
# last_name                   str
# date_of_birth    datetime64[us]
# gender                      str
# city                        str
# state                       str
# email                       str
# phone                    string
# dtype: object

# ===== Policy Transactions =====
# Index(['transaction_id', 'policy_id', 'customer_id', 'policy_start_date',
#        'policy_end_date', 'premium_amount', 'transaction_type'],
#       dtype='str')
#   transaction_id policy_id  ... premium_amount transaction_type
# 0        PTX0001    POL001  ...          18500           Active
# 1        PTX0002    POL002  ...          12400           Active
# 2        PTX0003    POL003  ...          22000           Active
# 3        PTX0004    POL004  ...          32000           Active
# 4        PTX0005    POL005  ...          15600           Active

# [5 rows x 7 columns]

# ===== Premium Transactions =====
# Index(['payment_id', 'policy_id', 'customer_id', 'payment_date',
#        'payment_amount', 'payment_method', 'payment_status'],
#       dtype='str')
#   payment_id policy_id  ... payment_method payment_status
# 0   PREM0001    POL001  ...            UPI     Successful
# 1   PREM0002    POL002  ...    Credit Card     Successful
# 2   PREM0003    POL003  ...     Debit Card     Successful
# 3   PREM0004    POL004  ...    Net Banking        Pending
# 4   PREM0005    POL005  ...           NEFT         Failed

# [5 rows x 7 columns]

# ===== Claim Transactions =====
# Index(['claim_id', 'policy_id', 'customer_id', 'claim_date', 'claim_type',
#        'claim_amount', 'claim_status'],
#       dtype='str')
#   claim_id policy_id customer_id  ...       claim_type claim_amount  claim_status
# 0  CTX0001    POL001     CUST001  ...  Hospitalization        45000      Approved
# 1  CTX0002    POL002     CUST002  ...   Vehicle Damage        75000  Under Review
# 2  CTX0003    POL003     CUST003  ...         Accident       120000      Rejected
# 3  CTX0004    POL004     CUST004  ...       Life Claim       185000      Approved
# 4  CTX0005    POL005     CUST005  ...  Hospitalization       250000      Approved

# [5 rows x 7 columns]

# ===== TABLES =====
#                    name
# 0                agents
# 1                claims
# 2             customers
# 3              payments
# 4              policies
# 5              branches
# 6   policy_transactions
# 7  premium_transactions
# 8    claim_transactions
# 9               weather
# agents: 8 rows
# claims: 3 rows
# customers: 12 rows
# payments: 12 rows
# policies: 12 rows
# branches: 100 rows
# policy_transactions: 120 rows
# premium_transactions: 150 rows
# claim_transactions: 120 rows
# weather: 24 rows

# [Done] exited with code=0 in 3.505 seconds

# ETL pipeline log:
# 2026-09-21 13:34:57,605 - INFO - ETL Pipeline Started
# 2026-09-21 13:34:59,064 - INFO - Data extraction completed successfully
# 2026-09-21 13:34:59,132 - INFO - Data transformation completed successfully
# 2026-09-21 13:34:59,175 - INFO - Data validation completed successfully
# 2026-09-21 13:34:59,460 - INFO - Data loaded into SQLite successfully
# 2026-09-21 13:34:59,460 - INFO - ETL Pipeline Completed Successfully
