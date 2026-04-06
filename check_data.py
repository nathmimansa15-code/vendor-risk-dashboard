import pandas as pd

files = [
    "data/vendors.csv",
    "data/vendor_compliance.csv",
    "data/vendor_financials.csv",
    "data/vendor_performance.csv",
    "data/vendor_incidents.csv"
]

for file in files:
    df = pd.read_csv(file)
    print(f"\n{file}")
    print(df.head())
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")