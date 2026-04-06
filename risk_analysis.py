import pandas as pd

vendors = pd.read_csv("data/vendors.csv")
compliance = pd.read_csv("data/vendor_compliance.csv")
financials = pd.read_csv("data/vendor_financials.csv")
performance = pd.read_csv("data/vendor_performance.csv")
incidents = pd.read_csv("data/vendor_incidents.csv")

df = vendors.merge(compliance, on="vendor_id") \
            .merge(financials, on="vendor_id") \
            .merge(performance, on="vendor_id") \
            .merge(incidents, on="vendor_id")

df["risk_score"] = (
    (100 - df["compliance_score"]) * 0.3 +
    df["financial_risk_score"] * 0.25 +
    (100 - df["delivery_score"]) * 0.2 +
    df["incident_count"] * 5 +
    df["sla_breach_count"] * 3
)

def categorize(score):
    if score > 70:
        return "High Risk"
    elif score > 40:
        return "Medium Risk"
    else:
        return "Low Risk"

df["risk_category"] = df["risk_score"].apply(categorize)

print("\nVendor Risk Analysis:\n")
print(df[["vendor_id", "vendor_name", "risk_score", "risk_category"]])

df.to_csv("outputs/vendor_risk_results.csv", index=False)

print("\nSaved to outputs/vendor_risk_results.csv")