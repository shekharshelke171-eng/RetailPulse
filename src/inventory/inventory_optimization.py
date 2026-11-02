
import pandas as pd
import numpy as np

# 1. Load dataset
df = pd.read_csv("data/featured_sales.csv")
df.columns = df.columns.str.strip()

# 2. Convert required columns
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)
df["Quantity"] = pd.to_numeric(
    df["Quantity"], errors="coerce"
)
df["TotalSales"] = pd.to_numeric(
    df["TotalSales"], errors="coerce"
)

# 3. Clean data
df = df.dropna(
    subset=["InvoiceDate", "StockCode", "Quantity", "TotalSales"]
)

df["Invoice"] = df["Invoice"].astype(str).str.strip()

# Remove cancelled invoices and return quantities
df = df[~df["Invoice"].str.upper().str.startswith("C")]
df = df[df["Quantity"] > 0].copy()

if df.empty:
    raise ValueError("No valid product sales found.")

# 4. Calculate product-level metrics
inventory = df.groupby(
    ["StockCode", "Description"], dropna=False
).agg(
    UnitsSold=("Quantity", "sum"),
    Revenue=("TotalSales", "sum"),
    NumberOfInvoices=("Invoice", "nunique"),
    FirstSale=("InvoiceDate", "min"),
    LastSale=("InvoiceDate", "max")
).reset_index()

# 5. Estimate average daily demand
days = max(
    1,
    (df["InvoiceDate"].max().normalize()
     - df["InvoiceDate"].min().normalize()).days + 1
)

inventory["AverageDailyDemand"] = (
    inventory["UnitsSold"] / days
)

# 6. Simple stock planning assumptions
# These are estimates, not actual warehouse stock levels.
lead_time_days = 7
safety_stock_days = 3

inventory["SuggestedReorderLevel"] = np.ceil(
    inventory["AverageDailyDemand"]
    * (lead_time_days + safety_stock_days)
).astype(int)

# 7. Rank products by units sold
inventory["DemandRank"] = inventory[
    "UnitsSold"
].rank(method="dense", ascending=False).astype(int)

inventory["DemandCategory"] = np.select(
    [
        inventory["DemandRank"] <= 20,
        inventory["DemandRank"] <= 100
    ],
    [
        "High Demand",
        "Medium Demand"
    ],
    default="Low Demand"
)

# 8. Sort and save
inventory = inventory.sort_values(
    "UnitsSold", ascending=False
)

inventory.to_csv(
    "data/inventory_recommendations.csv",
    index=False
)

print("\n--- Inventory Optimization Summary ---")
print("Products analyzed:", len(inventory))
print("Sales observation days:", days)

print("\n--- Top 10 Products by Units Sold ---")
print(
    inventory[
        [
            "StockCode",
            "Description",
            "UnitsSold",
            "Revenue",
            "AverageDailyDemand",
            "SuggestedReorderLevel",
            "DemandCategory"
        ]
    ].head(10).to_string(index=False)
)

print("\nInventory analysis completed!")
print("Saved: data/inventory_recommendations.csv")
