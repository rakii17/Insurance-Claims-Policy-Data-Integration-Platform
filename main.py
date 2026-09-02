import pandas as pd
from src.load import get_db_connection, load_to_sqlite
from src.extract_csv import extract_csv_data
from src.extract_excel import extract_excel_data
from src.extract_database import extract_database_data
from src.extract_api import get_weather_data
from src.validation import validate_dataframe

#extract
csv_data = extract_csv_data()
excel_data = extract_excel_data()
database_data = extract_database_data()
weather_df = get_weather_data()

#required columns for validate
required_columns = {
    "agents": ["agent_id"],
    "claims": ["policy_id", "customer_id"],
    "customers": ["customer_id", "first_name", "last_name"],
    "payments": ["payment_id", "policy_id", "customer_id"],
    "policies": ["policy_id", "customer_id"],
    "branches": ["branch_id"],
    "policy_transactions": ["transaction_id", "policy_id"],
    "premium_transactions": ["payment_id", "policy_id"],
    "claim_transactions": ["claim_id", "policy_id"]
}

#combine
datasets = {}

datasets.update(csv_data)
datasets.update(excel_data)
datasets.update(database_data)
datasets["weather"] = weather_df

for table_name, df in datasets.items():

    if table_name == "weather":
        continue

    validate_dataframe(
        df,
        table_name,
        required_columns[table_name]
    )

#load
conn = get_db_connection()
for table_name, df in datasets.items():
    load_to_sqlite(df, table_name, conn)
conn.close()

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

# #Output
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

# ===== customers.csv =====
#   customer_id first_name  ...                  email         phone
# 0     CUST001     Rajesh  ...             9876543210           NaN
# 1     CUST002      Priya  ...  priya.patel@email.com  9.876543e+09
# 2     CUST003       Amit  ...   amit.kumar@email.com  9.876543e+09
# 3     CUST004       Neha  ...   neha.verma@email.com  9.876543e+09
# 4     CUST005      Arjun  ...  arjun.reddy@email.com  9.876543e+09

# [5 rows x 9 columns]
# (12, 9)
# Index(['customer_id', 'first_name', 'last_name', 'date_of_birth', 'gender',
#        'city', 'state', 'email', 'phone'],
#       dtype='str')
# customer_id          str
# first_name           str
# last_name            str
# date_of_birth        str
# gender               str
# city                 str
# state                str
# email                str
# phone            float64
# dtype: object
# customer_id      0
# first_name       0
# last_name        0
# date_of_birth    0
# gender           0
# city             0
# state            0
# email            0
# phone            1
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
# claims: 12 rows
# customers: 12 rows
# payments: 12 rows
# policies: 12 rows
# branches: 100 rows
# policy_transactions: 120 rows
# premium_transactions: 150 rows
# claim_transactions: 120 rows
# weather: 24 rows

# [Done] exited with code=0 in 7.885 seconds

