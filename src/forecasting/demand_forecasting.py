
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 1. Load dataset
df = pd.read_csv("data/featured_sales.csv")

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
df["TotalSales"] = pd.to_numeric(df["TotalSales"], errors="coerce")

df = df.dropna(subset=["InvoiceDate", "TotalSales"])

# 2. Calculate monthly sales
df["MonthStart"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()

monthly = (
    df.groupby("MonthStart")["TotalSales"]
    .sum()
    .sort_index()
    .reset_index()
)

monthly.columns = ["Date", "Sales"]

print("Total months available:", len(monthly))
print(monthly.to_string(index=False))

# 3. Create time-based features
monthly["Month"] = monthly["Date"].dt.month
monthly["Year"] = monthly["Date"].dt.year
monthly["TimeIndex"] = np.arange(len(monthly))

monthly["Lag1"] = monthly["Sales"].shift(1)
monthly["Lag2"] = monthly["Sales"].shift(2)
monthly["Lag3"] = monthly["Sales"].shift(3)

model_data = monthly.dropna().reset_index(drop=True)

print("\nMonths available for modeling:", len(model_data))

# 4. Require enough data for a small baseline model
if len(model_data) < 8:
    raise ValueError(
        "Model साठी पुरेसा data नाही. "
        "किमान 11 monthly sales records आवश्यक आहेत."
    )

features = ["Month", "Year", "TimeIndex", "Lag1", "Lag2", "Lag3"]

# Keep the last 3 months for testing
test_size = 3
train = model_data.iloc[:-test_size]
test = model_data.iloc[-test_size:]

# 5. Train model
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(train[features], train["Sales"])

# 6. Evaluate
predictions = model.predict(test[features])

mae = mean_absolute_error(test["Sales"], predictions)
rmse = np.sqrt(mean_squared_error(test["Sales"], predictions))

print("\n--- Model Evaluation ---")
print("Training months:", len(train))
print("Testing months:", len(test))
print("MAE:", round(mae, 2))
print("RMSE:", round(rmse, 2))

comparison = pd.DataFrame({
    "Date": test["Date"].dt.strftime("%Y-%m"),
    "ActualSales": test["Sales"].values,
    "PredictedSales": predictions
})

print("\n--- Actual vs Predicted ---")
print(comparison.to_string(index=False))

# 7. Forecast next 3 months recursively
history = monthly["Sales"].tolist()
last_date = monthly["Date"].max()
future_results = []

for step in range(1, 4):
    future_date = last_date + pd.DateOffset(months=step)

    future_row = pd.DataFrame([{
        "Month": future_date.month,
        "Year": future_date.year,
        "TimeIndex": len(monthly) + step - 1,
        "Lag1": history[-1],
        "Lag2": history[-2],
        "Lag3": history[-3]
    }])

    predicted_sales = float(model.predict(future_row[features])[0])

    future_results.append({
        "Date": future_date.strftime("%Y-%m"),
        "PredictedSales": predicted_sales
    })

    history.append(predicted_sales)

forecast = pd.DataFrame(future_results)

print("\n--- Next 3 Months Forecast ---")
print(forecast.to_string(index=False))

# 8. Save results
comparison.to_csv("data/forecast_test_results.csv", index=False)
forecast.to_csv("data/sales_forecast.csv", index=False)

# 9. Plot historical sales and forecast
plt.figure(figsize=(12, 6))
plt.plot(monthly["Date"], monthly["Sales"], marker="o", label="Historical Sales")
plt.plot(test["Date"], predictions, marker="x", label="Test Predictions")

future_dates = pd.to_datetime(forecast["Date"])
plt.plot(
    future_dates,
    forecast["PredictedSales"],
    marker="o",
    linestyle="--",
    label="Next 3 Months Forecast"
)

plt.title("RetailPulse - Monthly Sales Forecast")
plt.xlabel("Month")
plt.ylabel("Total Sales")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("data/sales_forecast.png")
plt.show()

print("\nDemand Forecasting completed successfully!")
print("Saved: data/forecast_test_results.csv")
print("Saved: data/sales_forecast.csv")
print("Saved: data/sales_forecast.png")
