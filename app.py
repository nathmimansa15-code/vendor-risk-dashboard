import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Vendor 360 Risk Dashboard", layout="wide")

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
.main {
    background-color: #071126;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: white;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #111827, #1f2937);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
}
[data-testid="stMetricLabel"] {
    color: #cbd5e1;
}
[data-testid="stMetricValue"] {
    color: white;
}
div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 Vendor 360 Risk Intelligence Dashboard")
st.caption("An integrated vendor risk monitoring dashboard combining performance, compliance, incidents, and financial health.")

# -----------------------------
# LOAD FILES
# -----------------------------
DATA_FOLDER = "data"

files = {
    "vendors": "vendors.csv",
    "performance": "vendor_performance.csv",
    "compliance": "vendor_compliance.csv",
    "financials": "vendor_financials.csv",
    "incidents": "vendor_incidents.csv"
}

for _, file in files.items():
    path = os.path.join(DATA_FOLDER, file)
    if not os.path.exists(path):
        st.error(f"❌ Missing file: {file}")
        st.write("Available files:", os.listdir(DATA_FOLDER))
        st.stop()

vendors = pd.read_csv(os.path.join(DATA_FOLDER, files["vendors"]))
performance = pd.read_csv(os.path.join(DATA_FOLDER, files["performance"]))
compliance = pd.read_csv(os.path.join(DATA_FOLDER, files["compliance"]))
financials = pd.read_csv(os.path.join(DATA_FOLDER, files["financials"]))
incidents = pd.read_csv(os.path.join(DATA_FOLDER, files["incidents"]))

# -----------------------------
# CLEAN COLUMN NAMES
# -----------------------------
def clean(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    return df

vendors = clean(vendors)
performance = clean(performance)
compliance = clean(compliance)
financials = clean(financials)
incidents = clean(incidents)

# -----------------------------
# MERGE DATA
# -----------------------------
df = vendors.merge(performance, on="vendor_id", how="left") \
            .merge(compliance, on="vendor_id", how="left") \
            .merge(financials, on="vendor_id", how="left") \
            .merge(incidents, on="vendor_id", how="left")

# -----------------------------
# FILL MISSING VALUES SAFELY
# -----------------------------
for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
        df[col] = df[col].fillna(0)
    else:
        df[col] = df[col].fillna("Unknown")

# -----------------------------
# ENSURE EXPECTED COLUMNS EXIST
# -----------------------------
expected_numeric_cols = [
    "delivery_score",
    "quality_score",
    "sla_breach_count",
    "compliance_score",
    "issues_found",
    "financial_risk_score",
    "incident_count",
    "contract_value"
]

for col in expected_numeric_cols:
    if col not in df.columns:
        df[col] = 0

if "critical_vendor_flag" not in df.columns:
    df["critical_vendor_flag"] = "no"

# -----------------------------
# NORMALIZE FLAG
# -----------------------------
df["critical_vendor_flag"] = df["critical_vendor_flag"].astype(str).str.strip().str.lower()
df["critical_vendor_score"] = df["critical_vendor_flag"].apply(
    lambda x: 10 if x in ["yes", "y", "true", "1"] else 0
)

# -----------------------------
# RISK SUB-SCORES
# -----------------------------
df["performance_risk"] = (
    (100 - df["delivery_score"]) * 0.20 +
    (100 - df["quality_score"]) * 0.20 +
    df["sla_breach_count"] * 4
).round(2)

df["compliance_risk"] = (
    (100 - df["compliance_score"]) * 0.20 +
    df["issues_found"] * 3
).round(2)

df["financial_risk_component"] = (
    df["financial_risk_score"] * 0.15
).round(2)

df["incident_risk"] = (
    df["incident_count"] * 5
).round(2)

df["criticality_risk"] = df["critical_vendor_score"]

# -----------------------------
# TOTAL RISK SCORE
# -----------------------------
df["risk_score"] = (
    df["performance_risk"] +
    df["compliance_risk"] +
    df["financial_risk_component"] +
    df["incident_risk"] +
    df["criticality_risk"]
).round(2)

# -----------------------------
# RISK CATEGORY
# -----------------------------
def categorize(score):
    if score >= 60:
        return "High Risk"
    elif score >= 30:
        return "Medium Risk"
    else:
        return "Low Risk"

df["risk_category"] = df["risk_score"].apply(categorize)

# -----------------------------
# PRIMARY RISK DRIVER
# -----------------------------
def find_primary_driver(row):
    driver_scores = {
        "Performance": row["performance_risk"],
        "Compliance": row["compliance_risk"],
        "Financial": row["financial_risk_component"],
        "Incidents": row["incident_risk"],
        "Criticality": row["criticality_risk"]
    }
    return max(driver_scores, key=driver_scores.get)

df["primary_risk_driver"] = df.apply(find_primary_driver, axis=1)

# -----------------------------
# FILTERS
# -----------------------------
st.subheader("🔎 Filters")
f1, f2 = st.columns(2)

country_options = ["All"]
category_options = ["All"]

if "country" in df.columns:
    country_options += sorted(df["country"].astype(str).unique().tolist())
if "category" in df.columns:
    category_options += sorted(df["category"].astype(str).unique().tolist())

selected_country = f1.selectbox("Country", country_options)
selected_category = f2.selectbox("Category", category_options)

filtered_df = df.copy()

if selected_country != "All":
    filtered_df = filtered_df[filtered_df["country"] == selected_country]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

# -----------------------------
# KPI CARDS
# -----------------------------
st.subheader("📌 Key Metrics")
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Vendors", len(filtered_df))
k2.metric("High Risk Vendors", len(filtered_df[filtered_df["risk_category"] == "High Risk"]))
k3.metric("Avg Risk Score", round(filtered_df["risk_score"].mean(), 2) if len(filtered_df) > 0 else 0)
k4.metric("Critical Vendors", len(filtered_df[filtered_df["critical_vendor_flag"].isin(["yes", "y", "true", "1"])]))

# -----------------------------
# TOP 3 RISK VENDORS
# -----------------------------
st.subheader("🚨 Top 3 Risk Vendors")

top3 = filtered_df.sort_values(by="risk_score", ascending=False).head(3)

if len(top3) > 0:
    c1, c2, c3 = st.columns(3)
    cards = [c1, c2, c3]

    for idx, (_, row) in enumerate(top3.iterrows()):
        with cards[idx]:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #111827, #1f2937);
                padding: 18px;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.08);
                min-height: 180px;">
                <h4 style="color:white; margin-bottom:8px;">{row.get('vendor_name', 'Unknown Vendor')}</h4>
                <p style="color:#cbd5e1; margin:4px 0;"><b>Vendor ID:</b> {row.get('vendor_id', '')}</p>
                <p style="color:#cbd5e1; margin:4px 0;"><b>Risk Score:</b> {row.get('risk_score', 0)}</p>
                <p style="color:#cbd5e1; margin:4px 0;"><b>Risk Category:</b> {row.get('risk_category', '')}</p>
                <p style="color:#cbd5e1; margin:4px 0;"><b>Primary Driver:</b> {row.get('primary_risk_driver', '')}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("No vendors available for the selected filter.")

# -----------------------------
# RISK SCORE BY VENDOR
# -----------------------------
st.subheader("📊 Risk Score by Vendor")

if len(filtered_df) > 0 and "vendor_name" in filtered_df.columns:
    chart_df = filtered_df.sort_values(by="risk_score", ascending=False)[["vendor_name", "risk_score"]]
    st.bar_chart(chart_df.set_index("vendor_name"))
else:
    st.info("No chart data available.")

# -----------------------------
# RISK DISTRIBUTION
# -----------------------------
st.subheader("📉 Risk Distribution")
if len(filtered_df) > 0:
    st.bar_chart(filtered_df["risk_category"].value_counts())
else:
    st.info("No risk distribution available.")

# -----------------------------
# RISK DRIVERS TABLE
# -----------------------------
st.subheader("🔍 Risk Drivers")

risk_driver_cols = [col for col in [
    "vendor_name",
    "vendor_id",
    "risk_score",
    "primary_risk_driver",
    "incident_count",
    "issues_found",
    "compliance_score",
    "financial_risk_score",
    "delivery_score",
    "quality_score",
    "sla_breach_count"
] if col in filtered_df.columns]

st.dataframe(
    filtered_df.sort_values(by="risk_score", ascending=False)[risk_driver_cols],
    use_container_width=True
)

# -----------------------------
# VENDOR OVERVIEW
# -----------------------------
st.subheader("📋 Vendor Overview")

overview_cols = [col for col in [
    "vendor_id",
    "vendor_name",
    "country",
    "category",
    "contract_value",
    "delivery_score",
    "quality_score",
    "compliance_score",
    "issues_found",
    "financial_risk_score",
    "incident_count",
    "critical_vendor_flag",
    "risk_score",
    "risk_category",
    "primary_risk_driver"
] if col in filtered_df.columns]

st.dataframe(filtered_df[overview_cols], use_container_width=True)

# -----------------------------
# HIGH RISK VENDORS ONLY
# -----------------------------
st.subheader("⚠️ High Risk Vendors")

high_risk_df = filtered_df[filtered_df["risk_category"] == "High Risk"]

if len(high_risk_df) > 0:
    st.dataframe(
        high_risk_df.sort_values(by="risk_score", ascending=False)[overview_cols],
        use_container_width=True
    )
else:
    st.success("No high risk vendors found for the selected filters.")

# -----------------------------
# FOOTER INSIGHT
# -----------------------------
st.subheader("🧠 Dashboard Insight")

if len(filtered_df) > 0:
    highest_vendor = filtered_df.sort_values(by="risk_score", ascending=False).iloc[0]
    st.info(
        f"Highest current risk vendor is {highest_vendor.get('vendor_name', 'Unknown')} "
        f"with a risk score of {highest_vendor.get('risk_score', 0)}. "
        f"The primary risk driver is {highest_vendor.get('primary_risk_driver', 'N/A')}."
    )
else:
    st.info("No filtered data available to generate insights.")