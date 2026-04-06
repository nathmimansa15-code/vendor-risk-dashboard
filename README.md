# 📊 Vendor 360 Risk Intelligence Dashboard

## 🔍 Overview
This project presents an end-to-end vendor risk analytics solution built using Python and Streamlit. It helps organizations evaluate vendor performance across multiple dimensions and make data-driven decisions.

## 🎯 Objective
To move from manual vendor evaluation to a scalable, data-driven risk assessment system by:
- Automating risk scoring
- Visualizing vendor performance
- Enabling real-time decision making

## ⚙️ Tech Stack
- Python (Pandas, NumPy)
- Streamlit
- Data Visualization
- Risk Scoring Models

## 🚀 Features
- Vendor risk classification (Low / Medium / High)
- KPI tracking and performance insights
- Interactive dashboard with filters
- Drill-down analysis for individual vendors

## 📁 Project Structure
data/              # Raw dataset  
outputs/           # Processed results  
app.py             # Streamlit dashboard  
risk_analysis.py   # Risk scoring logic  
check_data.py      # Data validation  

## ▶️ How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
