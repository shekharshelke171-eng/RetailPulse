
import os
import mlflow
import mlflow.sklearn
import pandas as pd

from mlflow.models import infer_signature
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)
from sklearn.model_selection import train_test_split


# 1. Project configuration
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

DATA_PATH = os.path.join(
    PROJECT_ROOT, "data", "featured_sales.csv"
)

TRACKING_URI = "http://127.0.0.1:5000"

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment("RetailPulse_Churn_Experiment")


# 2. Load and clean dataset
df = pd.read_csv(DATA_PATH)
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

df["Invoice"] = df["Invoice"].astype(str).str.strip()
df = df[
    ~df["Invoice"].str.upper().str.startswith("C")
]
df = df[df["Quantity"] > 0].copy()

if df.empty:
    raise ValueError("No valid purchase records found.")


# 3. Create observation and label windows
last_date = df["InvoiceDate"].max()
label_cutoff = last_date - pd.Timedelta(days=90)

history = df[
    df["InvoiceDate"] <= label_cutoff
].copy()

label_period = df[
    (df["InvoiceDate"] > label_cutoff)
    & (df["InvoiceDate"] <= last_date)
].copy()

if history.empty:
    raise ValueError("Feature history is empty.")

reference_date = label_cutoff + pd.Timedelta(days=1)


# 4. Customer-level feature engineering
features = history.groupby("Customer ID").agg(
    Recency=("InvoiceDate", lambda x: (
        reference_date - x.max()
    ).days),
    Frequency=("Invoice", "nunique"),
    Monetary=("TotalSales", "sum"),
    TotalQuantity=("Quantity", "sum")
).reset_index()

active_customers = set(
    label_period["Customer ID"].unique()
)

features["Churn"] = (
    ~features["Customer ID"].isin(active_customers)
).astype(int)


# 5. Prepare training data
feature_columns = [
    "Recency",
    "Frequency",
    "Monetary",
    "TotalQuantity"
]

X = features[feature_columns]
y = features["Churn"]

if y.nunique() < 2 or y.value_counts().min() < 2:
    raise ValueError(
        "Both churn classes need at least two customers."
    )

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)


# 6. Train model and track experiment
with mlflow.start_run(run_name="RandomForest_Churn"):

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    # Evaluation metrics
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(
        y_test, predictions, zero_division=0
    )
    recall = recall_score(
        y_test, predictions, zero_division=0
    )
    f1 = f1_score(
        y_test, predictions, zero_division=0
    )

    # Log parameters
    mlflow.log_param("model_type", "RandomForestClassifier")
    mlflow.log_param("n_estimators", 200)
    mlflow.log_param("random_state", 42)
    mlflow.log_param("class_weight", "balanced")
    mlflow.log_param("test_size", 0.25)
    mlflow.log_param("feature_count", len(feature_columns))

    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)

    # Log dataset information
    mlflow.log_param("customer_count", len(features))
    mlflow.log_param("training_rows", len(X_train))
    mlflow.log_param("testing_rows", len(X_test))

    # Log classification report
    report = classification_report(
        y_test,
        predictions,
        target_names=["Active", "Churned"],
        zero_division=0
    )

    report_path = os.path.join(
        PROJECT_ROOT, "reports", "churn_classification_report.txt"
    )

    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)

    mlflow.log_artifact(report_path)

    # Log model artifact with input signature
    signature = infer_signature(X_train, model.predict(X_train))

    mlflow.sklearn.log_model(
        sk_model=model,
        name="churn_random_forest",
        signature=signature,
        input_example=X_train.head(5)
    )

    print("\n--- RetailPulse MLflow Results ---")
    print("Accuracy :", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall   :", round(recall, 4))
    print("F1 Score :", round(f1, 4))

    print("\nExperiment:", "RetailPulse_Churn_Experiment")
    print("Run ID:", mlflow.active_run().info.run_id)

    print("\nMLflow tracking completed successfully!")
