import os
import pandas as pd
import streamlit as st
import joblib

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Predictive Vendor Risk System", layout="wide")

# -----------------------------
# Title and Description
# -----------------------------
st.title("Predictive Vendor Risk Intelligence Dashboard")
st.markdown("End-to-end system that integrates vendor data and predicts high-risk vendors using machine learning.")

st.info("""
This system integrates vendor compliance, financial, incident, and performance data 
to predict future vendor risk using machine learning. 
It helps organizations proactively identify high-risk vendors and take action early.
""")

# -----------------------------
# Load Dataset
# -----------------------------
DATA_PATH = os.path.join("data", "final_vendor_data.csv")

if not os.path.exists(DATA_PATH):
    st.error("Dataset not found. Run prepare_data.py first.")
    st.stop()

df = pd.read_csv(DATA_PATH)

# -----------------------------
# Create Risk Flag
# -----------------------------
df["risk_flag"] = (
    (df["financial_risk_score"] >= 70) |
    (df["incident_count"] >= 3) |
    (df["sla_breach_count"] >= 2) |
    (df["delivery_score"] < 60) |
    (df["quality_score"] < 60)
).astype(int)

# -----------------------------
# Key Metrics
# -----------------------------
st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Total Vendors", len(df))
col2.metric("High Risk Vendors", int(df["risk_flag"].sum()))
col3.metric("Avg Financial Risk", round(df["financial_risk_score"].mean(), 2))

# -----------------------------
# Risk Distribution
# -----------------------------
st.subheader("Risk Distribution")

risk_counts = df["risk_flag"].value_counts().rename({
    0: "Low / Medium Risk",
    1: "High Risk"
})

st.caption("Distribution of vendors by predicted risk level")
st.bar_chart(risk_counts)

# -----------------------------
# Vendor Data Preview
# -----------------------------
st.subheader("Vendor Data Preview")
st.dataframe(df.head(10), use_container_width=True)

# -----------------------------
# High Risk Vendors
# -----------------------------
st.subheader("High Risk Vendors")
st.caption("Vendors requiring immediate attention based on risk indicators")

high_risk_df = df[df["risk_flag"] == 1]

if not high_risk_df.empty:
    st.dataframe(
        high_risk_df[
            [
                "vendor_name",
                "financial_risk_score",
                "incident_count",
                "delivery_score",
                "quality_score",
                "sla_breach_count"
            ]
        ],
        use_container_width=True
    )
else:
    st.success("No high-risk vendors identified in the dataset.")

# -----------------------------
# Load ML Model
# -----------------------------
MODEL_PATH = os.path.join("models", "risk_model.pkl")
FEATURE_PATH = os.path.join("models", "feature_columns.pkl")

if not os.path.exists(MODEL_PATH) or not os.path.exists(FEATURE_PATH):
    st.warning("Model not found. Run train_model.py first.")
    st.stop()

model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(FEATURE_PATH)

# -----------------------------
# Prediction Section
# -----------------------------
st.subheader("Predict Vendor Risk")

col1, col2 = st.columns(2)

with col1:
    issues_found = st.number_input("Issues Found", min_value=0, value=1)
    annual_revenue = st.number_input("Annual Revenue", min_value=0.0, value=500000.0)
    profit_margin = st.number_input("Profit Margin", value=12.5)
    financial_risk_score = st.number_input("Financial Risk Score", min_value=0.0, max_value=100.0, value=50.0)

with col2:
    incident_count = st.number_input("Incident Count", min_value=0, value=1)
    delivery_score = st.number_input("Delivery Score", min_value=0.0, max_value=100.0, value=75.0)
    quality_score = st.number_input("Quality Score", min_value=0.0, max_value=100.0, value=80.0)
    sla_breach_count = st.number_input("SLA Breach Count", min_value=0, value=0)

if st.button("Predict Risk"):
    input_data = pd.DataFrame([{
        "issues_found": issues_found,
        "annual_revenue": annual_revenue,
        "profit_margin": profit_margin,
        "financial_risk_score": financial_risk_score,
        "incident_count": incident_count,
        "delivery_score": delivery_score,
        "quality_score": quality_score,
        "sla_breach_count": sla_breach_count
    }])

    input_data = input_data[feature_columns]

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    if prediction == 1:
        st.markdown("### 🚨 High Risk Vendor Detected")
    else:
        st.markdown("### ✅ Vendor is Low / Medium Risk")

    st.metric("Risk Probability", f"{probability:.2%}")

# -----------------------------
# Model Evaluation
# -----------------------------
cm_path = os.path.join("models", "confusion_matrix.png")

if os.path.exists(cm_path):
    st.subheader("Model Evaluation")
    st.image(cm_path, caption="Confusion Matrix")