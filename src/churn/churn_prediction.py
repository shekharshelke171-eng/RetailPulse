
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

# 1. Load data
df = pd.read_csv("data/featured_sales.csv")

# 2. Clean and convert columns
df.columns = df.columns.str.strip()

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)
df["Customer ID"] = pd.to_numeric(
    df["Customer ID"], errors="coerce"
)
df["Quantity"] = pd.to_numeric(
    df["Quantity"], errors="coerce"
)
df["TotalSales"] = pd.to_numeric(
    df["TotalSales"], errors="coerce"
)

df = df.dropna(
    subset=[
        "Customer ID",
        "InvoiceDate",
        "Quantity",
        "TotalSales",
        "Invoice"
    ]
)

# Remove cancelled invoices
df["Invoice"] = df["Invoice"].astype(str).str.strip()
df = df[~df["Invoice"].str.upper().str.startswith("C")]

# Keep positive-quantity purchases for customer activity features
df = df[df["Quantity"] > 0].copy()

if df.empty:
    raise ValueError("Valid purchase records were not found.")

# 3. Set observation and label windows
last_date = df["InvoiceDate"].max()
label_cutoff = last_date - pd.Timedelta(days=90)

# Features use transactions up to the cutoff
history = df[df["InvoiceDate"] <= label_cutoff].copy()

# Labels use the following 90 days
label_period = df[
    (df["InvoiceDate"] > label_cutoff)
    & (df["InvoiceDate"] <= last_date)
].copy()

if history.empty:
    raise ValueError(
        "Feature period is empty. More historical data is needed."
    )

# 4. Build customer-level features
reference_date = label_cutoff + pd.Timedelta(days=1)

features = history.groupby("Customer ID").agg(
    Recency=("InvoiceDate", lambda x: (
        reference_date - x.max()
    ).days),
    Frequency=("Invoice", "nunique"),
    Monetary=("TotalSales", "sum"),
    TotalQuantity=("Quantity", "sum")
).reset_index()

# 5. Create target label
# Churn = no recorded purchase during the next 90 days
active_customers = set(label_period["Customer ID"].unique())

features["Churn"] = (
    ~features["Customer ID"].isin(active_customers)
).astype(int)

print("\n--- Churn Dataset Summary ---")
print("Customers:", len(features))
print("\nChurn labels:")
print(features["Churn"].value_counts().rename({
    0: "Active in next 90 days",
    1: "No purchase in next 90 days"
}))

# 6. Prepare ML data
feature_columns = [
    "Recency", "Frequency", "Monetary", "TotalQuantity"
]

X = features[feature_columns]
y = features["Churn"]

if y.nunique() < 2 or y.value_counts().min() < 2:
    raise ValueError(
        "दोन्ही churn classes मध्ये पुरेसे customers नाहीत. "
        "अधिक data किंवा वेगळी time window आवश्यक आहे."
    )

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# 7. Train classifier
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# 8. Evaluate
predictions = model.predict(X_test)

print("\n--- Model Evaluation ---")
print("Accuracy:", round(accuracy_score(y_test, predictions), 3))
print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    target_names=["Active", "Churned"],
    zero_division=0
))

# 9. Predict churn risk for customers
features["ChurnRiskProbability"] = model.predict_proba(X)[
    :, list(model.classes_).index(1)
]

features["ChurnRisk"] = pd.cut(
    features["ChurnRiskProbability"],
    bins=[-0.001, 0.4, 0.7, 1.001],
    labels=["Low", "Medium", "High"]
)

features = features.sort_values(
    "ChurnRiskProbability", ascending=False
)

features.to_csv("data/customer_churn_predictions.csv", index=False)

print("\n--- Highest Churn Risk Customers ---")
print(
    features[
        [
            "Customer ID",
            "Recency",
            "Frequency",
            "ChurnRiskProbability",
            "ChurnRisk"
        ]
    ].head(10).to_string(index=False)
)

print("\nChurn prediction completed!")
print("Saved: data/customer_churn_predictions.csv")
