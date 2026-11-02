
import pandas as pd

df = pd.read_csv("data/featured_sales.csv")

print("Dataset shape:", df.shape)
print("\nColumns:", df.columns.tolist())

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)

print("\nValid dates:", df["InvoiceDate"].notna().sum())
print("Invalid dates:", df["InvoiceDate"].isna().sum())

print("\nEarliest date:", df["InvoiceDate"].min())
print("Latest date:", df["InvoiceDate"].max())

print("\nMonthly record count:")
print(
    df.dropna(subset=["InvoiceDate"])
      .groupby(df["InvoiceDate"].dt.to_period("M"))
      .size()
      .to_string()
)

print("\nUnique months:",
      df["InvoiceDate"].dt.to_period("M").nunique())
