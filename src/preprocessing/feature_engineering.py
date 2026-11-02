
import pandas as pd

# Load Excel dataset
df = pd.read_excel("data/sales.xlsx")

# Clean column names
df.columns = df.columns.str.strip()

# Convert data types
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)

df["Quantity"] = pd.to_numeric(
    df["Quantity"], errors="coerce"
)

df["Price"] = pd.to_numeric(
    df["Price"], errors="coerce"
)

# Feature Engineering
df["TotalSales"] = df["Quantity"] * df["Price"]

df["Year"] = df["InvoiceDate"].dt.year
df["Month"] = df["InvoiceDate"].dt.month
df["Day"] = df["InvoiceDate"].dt.day
df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()
df["YearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)

# Display results
print(df.head())
print("\nNew columns:")
print(df.columns.tolist())

# Save engineered dataset
df.to_csv(
    "data/featured_sales.csv",
    index=False
)

print("\nFeature Engineering completed successfully!")
