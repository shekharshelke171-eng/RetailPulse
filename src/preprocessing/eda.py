
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load feature-engineered dataset
df = pd.read_csv("data/featured_sales.csv")

# 2. Basic dataset information
print("\n--- Dataset Information ---")
print("Shape:", df.shape)
print("\nMissing Values:")
print(df.isnull().sum())

# 3. Sales summary
print("\n--- Sales Summary ---")
print("Total Sales:", round(df["TotalSales"].sum(), 2))
print("Total Quantity Sold:", df["Quantity"].sum())
print("Unique Products:", df["StockCode"].nunique())
print("Unique Countries:", df["Country"].nunique())
print("Unique Invoices:", df["Invoice"].nunique())

# 4. Monthly sales trend
monthly_sales = (
    df.groupby("YearMonth")["TotalSales"]
    .sum()
    .sort_index()
)

plt.figure(figsize=(12, 5))
monthly_sales.plot()
plt.title("RetailPulse - Monthly Sales Trend")
plt.xlabel("Year-Month")
plt.ylabel("Total Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("data/monthly_sales_trend.png")
plt.close()

# 5. Top 10 products by sales
top_products = (
    df.groupby("Description")["TotalSales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n--- Top 10 Products by Sales ---")
print(top_products)

plt.figure(figsize=(10, 6))
top_products.sort_values().plot(kind="barh")
plt.title("Top 10 Products by Sales")
plt.xlabel("Total Sales")
plt.ylabel("Product")
plt.tight_layout()
plt.savefig("data/top_products.png")
plt.close()

# 6. Top 10 countries by sales
top_countries = (
    df.groupby("Country")["TotalSales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n--- Top 10 Countries by Sales ---")
print(top_countries)

plt.figure(figsize=(10, 6))
top_countries.sort_values().plot(kind="barh")
plt.title("Top 10 Countries by Sales")
plt.xlabel("Total Sales")
plt.ylabel("Country")
plt.tight_layout()
plt.savefig("data/top_countries.png")
plt.close()

# 7. Save analysis summaries
monthly_sales.to_csv("data/monthly_sales_summary.csv")
top_products.to_csv("data/top_products_summary.csv")
top_countries.to_csv("data/top_countries_summary.csv")

print("\nEDA completed successfully!")
print("Charts and summary files saved in the data folder.")
