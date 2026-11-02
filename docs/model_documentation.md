\# RetailPulse - Model Documentation



\## 1. Overview



RetailPulse is an AI-powered retail analytics platform that supports customer segmentation, churn prediction, demand forecasting and inventory optimization.



\## 2. Customer Segmentation



\*\*Technique:\*\* RFM Analysis



RFM stands for:



\- Recency: How recently a customer purchased.

\- Frequency: How often a customer purchases.

\- Monetary: How much a customer spends.



\### Customer Segments



| Segment | Customers |

|---|---:|

| Champions | 1,085 |

| Loyal Customers | 804 |

| At Risk | 699 |

| Recent Customers | 359 |

| Others | 1,367 |

| Total | 4,314 |



\## 3. Customer Churn Prediction



The churn module analyzes customer purchase behavior to estimate future purchase activity.



\### Verified Results



\- Total customer records: 3,379

\- Active in next 90 days: 1,942

\- No purchase in next 90 days: 1,437

\- Model accuracy: 63.3%



\### Churn Risk Distribution



| Risk Level | Customers |

|---|---:|

| Low | 1,798 |

| Medium | 352 |

| High | 1,229 |



\## 4. Demand Forecasting



The forecasting module analyzes historical sales data to estimate future sales demand.



\### Evaluation Results



\- Training periods: 7 months

\- Testing periods: 3 months

\- Total modeled periods: 10 months

\- MAE: 477,198.11

\- RMSE: 499,340.66

\- R-squared: -0.3352



Note: The negative R-squared indicates that the current forecasting model requires further improvement.



\## 5. Inventory Optimization



The inventory module analyzes product sales and generates reorder recommendations.



Example:

\- Top reorder recommendation: StockCode 85123A

\- Recommended reorder quantity: 1,564 units



\## 6. Model Limitations



\- Forecasting performance requires further tuning.

\- Missing customer IDs limit customer-level analysis.

\- Predictions depend on the quality and availability of historical transaction data.



\## 7. Conclusion



The analytical modules provide insights into customer behavior, sales trends, churn risk and inventory requirements. Results should be interpreted as analytical estimates rather than guaranteed business outcomes.
