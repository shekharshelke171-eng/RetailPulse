# RetailPulse - User Guide

## 1. Introduction

RetailPulse is a Streamlit-based retail analytics dashboard designed to help users understand sales performance, customer behavior, demand patterns and inventory requirements.

## 2. Launching the Dashboard

1. Open PowerShell in the RetailPulse project directory.
2. Ensure the required Python dependencies are installed.
3. Run: `streamlit run dashboard/app.py`
4. Open the local URL displayed in the terminal.

## 3. Dashboard Pages

1. Home - Dashboard introduction and navigation.
2. Executive Dashboard - Key business performance indicators.
3. Sales Analytics - Revenue and sales trends.
4. Customer Analytics - Customer purchasing behavior.
5. Customer Segmentation - RFM-based customer groups.
6. Customer Churn - Customer activity predictions and risk categories.
7. Inventory - Inventory insights and reorder recommendations.
8. Country Analysis - Country-wise sales performance.
9. Product Analytics - Product-level sales performance.
10. Demand Forecast - Historical sales and forecasting results.
11. Business Insights - Analytical business insights.
12. CSV Data Explorer - Explore available CSV datasets.

## 4. Using the Dashboard

- Navigate through pages using the sidebar.
- Review charts, metrics and tables.
- Use available filters where provided.
- Explore customer, product and country-level results.
- Review forecast and inventory recommendations.

## 5. Data Requirements

The dashboard uses datasets stored in the `data` directory.

Main dataset: `featured_sales.csv`

Other analytical CSV files support individual dashboard pages.

## 6. Important Notes

- Dashboard results depend on available datasets.
- Predictions are estimates, not guaranteed outcomes.
- Keep required data files in their expected locations.
- Never upload private credentials or environment secrets to GitHub.

## 7. Conclusion

RetailPulse provides an interactive interface for exploring retail sales, customers, products, forecasts and inventory analytics.