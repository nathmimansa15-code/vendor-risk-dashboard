import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------- Page Config ----------
st.set_page_config(
    page_title="Vendor 360 Risk Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------- Styling ----------
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
}
.dashboard-title {
    font-size: 40px;
    font-weight: 800;
    color: #f9fafb;
}
.dashboard-subtitle {
    font-size: 18px;
    color: #cbd5e1;
    margin-bottom: 1.5rem;
}
.section-header {
    font-size: 24px;
    font-weight: 700;
    color: #f8fafc;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.metric-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 18px;
    border-radius: 16px;
}
.metric-label {
    font-size: 14px;
    color: #cbd5e1;
}
.metric-value {
    font-size: 36px;
    font-weight: 800;
    color: #60a5fa;
}
.info-card {
    background: linear-gradient(135deg, #172554, #1e3a8a);
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 1rem;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- Load Data ----------
file_path = "outputs/vendor_risk_results.csv"

if not os.path.exists(file_path):
    st.error("❌ Output file not found. Run risk_analysis.py first.")
    st.stop()

df = pd.read_csv(file_path)

# ---------- Header ----------
st.markdown('<div class="dashboard-title">Vendor 360 Risk Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">Interactive analytics platform for monitoring vendor risk</div>', unsafe_allow_html=True)

# ---------- Banner ----------
high_risk_total = len(df[df["risk_category"] == "High Risk"])

if high_risk_total > 0:
    banner_text = f"🚨 {high_risk_total} vendor(s) require immediate attention"
else:
    banner_text = "✅ No high-risk vendors detected"

st.markdown(f"""
<div style="background: linear-gradient(90deg, #1e3a8a, #0f172a);
padding: 14px; border-radius: 12px; color:white; margin-bottom: 15px;">
{banner_text}
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.title("⚙️ Filters")

risk_filter = st.sidebar.selectbox(
    "Risk Category",
    ["All"] + sorted(df["risk_category"].dropna().unique().tolist())
)

vendor_filter = st.sidebar.selectbox(
    "Vendor",
    ["All"] + sorted(df["vendor_name"].dropna().unique().tolist())
)

search = st.sidebar.text_input("🔍 Search Vendor")

filtered_df = df.copy()

if risk_filter != "All":
    filtered_df = filtered_df[filtered_df["risk_category"] == risk_filter]

if vendor_filter != "All":
    filtered_df = filtered_df[filtered_df["vendor_name"] == vendor_filter]

if search:
    filtered_df = filtered_df[
        filtered_df["vendor_name"].astype(str).str.contains(search, case=False, na=False)
    ]

# ---------- Metrics ----------
total_vendors = len(filtered_df)
high_risk = len(filtered_df[filtered_df["risk_category"] == "High Risk"])
avg_score = round(filtered_df["risk_score"].mean(), 2) if len(filtered_df) > 0 else 0

st.markdown('<div class="section-header">Key Metrics</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

c1.markdown(f'<div class="metric-card"><div class="metric-label">Total Vendors</div><div class="metric-value">{total_vendors}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="metric-card"><div class="metric-label">High Risk Vendors</div><div class="metric-value">{high_risk}</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="metric-card"><div class="metric-label">Avg Risk Score</div><div class="metric-value">{avg_score}</div></div>', unsafe_allow_html=True)

# ---------- Insight ----------
st.progress(min(avg_score / 100, 1.0))

if avg_score > 60:
    st.error("⚠️ High vendor risk detected")
elif avg_score > 40:
    st.warning("⚠️ Moderate vendor risk")
else:
    st.success("✅ Vendor ecosystem stable")

# ---------- Layout ----------
left, right = st.columns([2, 1])

# ---------- Left ----------
with left:
    st.markdown('<div class="section-header">Vendor Overview</div>', unsafe_allow_html=True)
    st.dataframe(filtered_df, use_container_width=True)

    st.markdown('<div class="section-header">Risk Distribution</div>', unsafe_allow_html=True)

    if len(filtered_df) > 0:
        risk_counts = filtered_df["risk_category"].value_counts().reset_index()
        risk_counts.columns = ["Risk", "Count"]

        fig = px.bar(
            risk_counts,
            x="Risk",
            y="Count",
            color="Risk",
            color_discrete_map={
                "High Risk": "#ef4444",
                "Medium Risk": "#f59e0b",
                "Low Risk": "#22c55e"
            }
        )

        fig.update_layout(
            plot_bgcolor="#0b1220",
            paper_bgcolor="#0b1220",
            font_color="white"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-header">Top Risk Vendors</div>', unsafe_allow_html=True)

        top10 = filtered_df.sort_values("risk_score", ascending=False).head(10)

        fig_top = px.bar(
            top10,
            x="vendor_name",
            y="risk_score",
            color="risk_category",
            color_discrete_map={
                "High Risk": "#ef4444",
                "Medium Risk": "#f59e0b",
                "Low Risk": "#22c55e"
            }
        )

        fig_top.update_layout(
            plot_bgcolor="#0b1220",
            paper_bgcolor="#0b1220",
            font_color="white"
        )

        st.plotly_chart(fig_top, use_container_width=True)

# ---------- Right ----------
with right:
    st.markdown('<div class="section-header">Insights</div>', unsafe_allow_html=True)

    if len(filtered_df) > 0:
        top = filtered_df.sort_values("risk_score", ascending=False).iloc[0]

        st.markdown(f"""
        <div class="info-card">
        <b>Top Risk Vendor</b><br><br>
        {top['vendor_name']}<br>
        Score: {round(top['risk_score'], 2)}<br>
        Category: {top['risk_category']}
        </div>
        """, unsafe_allow_html=True)

# ---------- Drilldown ----------
st.markdown('<div class="section-header">Vendor Drilldown</div>', unsafe_allow_html=True)

if len(filtered_df) > 0:
    selected = st.selectbox("Select Vendor", filtered_df["vendor_name"].unique())
    v = filtered_df[filtered_df["vendor_name"] == selected].iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Vendor Details")
        st.dataframe(v.to_frame(name="Value"))

    with col2:
        st.write("### Risk Breakdown")

        risk_cols = [
            "delivery_risk",
            "compliance_risk",
            "financial_risk",
            "performance_risk",
            "incident_risk"
        ]

        if all(col in df.columns for col in risk_cols):
            breakdown = pd.DataFrame({
                "Factor": ["Delivery", "Compliance", "Financial", "Performance", "Incidents"],
                "Score": [v[col] for col in risk_cols]
            })

            fig_pie = px.pie(
                breakdown,
                names="Factor",
                values="Score",
                hole=0.4
            )

            fig_pie.update_layout(
                plot_bgcolor="#0b1220",
                paper_bgcolor="#0b1220",
                font_color="white"
            )

            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Detailed risk breakdown not available in current dataset.")