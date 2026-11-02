\# RetailPulse - System Architecture



\## 1. Introduction



RetailPulse is an AI-powered retail analytics and demand forecasting platform. It analyzes retail transaction data and provides insights into sales performance, customer behaviour, customer segmentation, churn prediction, demand forecasting, and inventory planning.



\## 2. System Architecture



The project follows a modular Python-based architecture.



\### Main Components



1\. \*\*Data Layer\*\*

&#x20;  - Stores retail transaction datasets and processed CSV files.

&#x20;  - Contains customer, product, sales, forecast, and inventory data.



2\. \*\*Data Processing Layer\*\*

&#x20;  - Cleans and transforms retail data.

&#x20;  - Performs exploratory data analysis and feature engineering.

&#x20;  - Generates summary datasets for dashboard visualization.



3\. \*\*Machine Learning Layer\*\*

&#x20;  - Customer churn prediction using Random Forest Classification.

&#x20;  - Demand forecasting using Random Forest Regression.

&#x20;  - Customer segmentation using RFM analysis.

&#x20;  - Inventory recommendations based on product sales information.



4\. \*\*Dashboard Layer\*\*

&#x20;  - Developed using Streamlit.

&#x20;  - Uses Pandas for data processing.

&#x20;  - Uses Plotly for interactive visualizations.

&#x20;  - Presents business insights through 12 dashboard modules.



\## 3. Data Flow



```text

Retail Transaction Dataset

&#x20;         |

&#x20;         v

Data Preprocessing

&#x20;         |

&#x20;         v

Feature Engineering and EDA

&#x20;         |

&#x20;         v

Analytics and ML Modules

&#x20;         |

&#x20;         v

Processed CSV Outputs

&#x20;         |

&#x20;         v

Streamlit Dashboard

&#x20;         |

&#x20;         v

Business Insights

```



\## 4. Project Modules



| Module | Responsibility |

|---|---|

| Preprocessing | Data cleaning and feature engineering |

| EDA | Exploratory data analysis |

| Segmentation | RFM customer segmentation |

| Churn | Customer churn prediction |

| Forecasting | Sales demand forecasting |

| Inventory | Inventory recommendations |

| Dashboard | Interactive analytics and reporting |



\## 5. Technology Stack



\- Programming Language: Python

\- Dashboard: Streamlit

\- Data Processing: Pandas, NumPy

\- Machine Learning: Scikit-learn

\- Visualization: Plotly, Matplotlib

\- Data Storage: CSV files



\## 6. Application Entry Point



The main dashboard application is located at:



`dashboard/app.py`



Run the application using:



```bash

streamlit run dashboard/app.py

```



\## 7. Current Implementation Status



The Streamlit dashboard and its 12 modules are implemented. Data processing and analytics scripts are available in the `src/` directory.



Docker, Kubernetes, and MLflow are planned extensions and should not be considered implemented components yet.
