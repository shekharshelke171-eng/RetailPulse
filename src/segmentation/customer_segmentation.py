
import pandas as pd

# Load feature-engineered dataset
df = pd.read_csv("data/featured_sales.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Convert data types
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)
df["Customer ID"] = pd.to_numeric(
    df["Customer ID"], errors="coerce"
)
df["TotalSales"] = pd.to_numeric(
    df["TotalSales"], errors="coerce"
)

# Remove records without customer ID or valid date
df = df.dropna(
    subset=["Customer ID", "InvoiceDate", "TotalSales", "Invoice"]
)

# Exclude cancelled invoices (Online Retail II often uses
# invoice numbers starting with C for cancellations)
df["Invoice"] = df["Invoice"].astype(str).str.strip()
df = df[~df["Invoice"].str.upper().str.startswith("C")]

# Reference date: one day after the latest transaction
reference_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

# Calculate RFM metrics
rfm = df.groupby("Customer ID").agg(
    Recency=("InvoiceDate", lambda x: (
        reference_date - x.max()
    ).days),
    Frequency=("Invoice", "nunique"),
    Monetary=("TotalSales", "sum")
).reset_index()

# Score customers from 1 to 5
rfm["R_Score"] = pd.qcut(
    rfm["Recency"].rank(method="first"),
    5,
    labels=[5, 4, 3, 2, 1]
).astype(int)

rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

# Combine RFM scores
rfm["RFM_Score"] = (
    rfm["R_Score"].astype(str)
    + rfm["F_Score"].astype(str)
    + rfm["M_Score"].astype(str)
)

# Basic customer segmentation
def segment_customer(row):
    if row["R_Score"] >= 4 and row["F_Score"] >= 4:
        return "Champions"
    elif row["R_Score"] >= 3 and row["F_Score"] >= 3:
        return "Loyal Customers"
    elif row["R_Score"] >= 4:
        return "Recent Customers"
    elif row["R_Score"] <= 2 and row["F_Score"] >= 3:
        return "At Risk"
    else:
        return "Others"

rfm["Customer_Segment"] = rfm.apply(
    segment_customer, axis=1
)

# Save results
rfm.to_csv("data/customer_rfm_segments.csv", index=False)

print("\n--- RFM Analysis Summary ---")
print("Total customers:", len(rfm))
print("\nCustomer segments:")
print(rfm["Customer_Segment"].value_counts())

print("\nTop 10 customers by Monetary value:")
print(
    rfm.sort_values("Monetary", ascending=False)
    .head(10)
    .to_string(index=False)
)

print("\nRFM Analysis completed successfully!")
print("Saved: data/customer_rfm_segments.csv")
