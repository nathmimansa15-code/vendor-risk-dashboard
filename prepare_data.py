import pandas as pd
import os

base_path = "data"

# Load CSV files (IMPORTANT CHANGE)
vendors = pd.read_csv(os.path.join(base_path, "vendors.csv"))
compliance = pd.read_csv(os.path.join(base_path, "vendor_compliance.csv"))
financials = pd.read_csv(os.path.join(base_path, "vendor_financials.csv"))
incidents = pd.read_csv(os.path.join(base_path, "vendor_incidents.csv"))
performance = pd.read_csv(os.path.join(base_path, "vendor_performance.csv"))

# Print columns (VERY IMPORTANT)
print("Vendors:", vendors.columns)
print("Compliance:", compliance.columns)
print("Financials:", financials.columns)
print("Incidents:", incidents.columns)
print("Performance:", performance.columns)

# Merge (we may fix key next)
df = vendors.merge(compliance, on="vendor_id", how="left")
df = df.merge(financials, on="vendor_id", how="left")
df = df.merge(incidents, on="vendor_id", how="left")
df = df.merge(performance, on="vendor_id", how="left")

# Save final dataset
df.to_csv(os.path.join(base_path, "final_vendor_data.csv"), index=False)

print("✅ final_vendor_data.csv created successfully")