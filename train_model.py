import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay

# -----------------------------
# Load merged dataset
# -----------------------------
DATA_PATH = os.path.join("data", "final_vendor_data.csv")
df = pd.read_csv(DATA_PATH)

print("Columns in dataset:")
print(df.columns.tolist())

# -----------------------------
# Create target variable manually
# High Risk = 1 if vendor shows multiple warning signs
# -----------------------------
df["target"] = (
    (df["financial_risk_score"] >= 70) |
    (df["incident_count"] >= 3) |
    (df["sla_breach_count"] >= 2) |
    (df["delivery_score"] < 60) |
    (df["quality_score"] < 60)
).astype(int)

# -----------------------------
# Select features
# -----------------------------
feature_columns = [
    "issues_found",
    "annual_revenue",
    "profit_margin",
    "financial_risk_score",
    "incident_count",
    "delivery_score",
    "quality_score",
    "sla_breach_count"
]

X = df[feature_columns]
y = df["target"]

# Handle missing values
X = X.fillna(X.mean())

# -----------------------------
# Split data
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------------
# Train model
# -----------------------------
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# -----------------------------
# Predictions
# -----------------------------
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# -----------------------------
# Save confusion matrix
# -----------------------------
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot()
plt.savefig("models/confusion_matrix.png")
plt.close()

# -----------------------------
# Save model and features
# -----------------------------
joblib.dump(model, "models/risk_model.pkl")
joblib.dump(feature_columns, "models/feature_columns.pkl")

print("\n✅ Model saved successfully in models folder")