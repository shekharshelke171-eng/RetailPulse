
﻿# RetailPulse - AI-Powered Customer Analytics & Demand Forecasting Platform

## Project Overview
RetailPulse is an AI-powered retail analytics and machine learning platform designed to analyze sales performance, understand customer behaviour, predict customer churn, forecast product demand, and support inventory planning.

It provides an interactive Streamlit dashboard with multiple analytics modules.

## Key Features

- Exploratory Data Analysis (EDA)
- Data Cleaning and Feature Engineering
- RFM-Based Customer Segmentation
- Customer Churn Prediction
- Sales Demand Forecasting
- Inventory Optimization
- Country-wise Sales Analysis
- Product Performance Analysis
- Interactive Streamlit Dashboard
- CSV Data Explorer

## Technologies Used

- Python
- Pandas and NumPy
- Scikit-learn
- Streamlit
- Plotly
- Matplotlib and Seaborn
- Machine Learning


## Project Structure

RetailPulse/
├── .github/
│   └── workflows/
├── dashboard/
│   └── app.py
├── data/
│   ├── featured_sales.csv
│   └── analytics outputs
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── installation_guide.md
│   ├── model_documentation.md
│   ├── user_guide.md
│   └── RetailPulse_Project_Report.md
├── reports/
│   └── churn_classification_report.txt
├── scripts/
│   ├── check_dates.py
│   └── inspect_data.py
├── src/
│   ├── preprocessing/
│   ├── segmentation/
│   ├── forecasting/
│   ├── churn/
│   └── inventory/
├── requirements.txt
├── style.css
├── .gitignore
└── README.md

## Installation

1. Clone or download the project.
2. Open the RetailPulse directory.
3. Create a virtual environment:

```bash
python -m venv .venv
```

4. Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Dashboard

Run from the main RetailPulse directory:

```bash
streamlit run dashboard/app.py
```

## Dashboard Modules

1. Home
2. Executive Dashboard
3. Sales Analytics
4. Customer Analytics
5. Customer Segmentation
6. Customer Churn
7. Inventory
8. Country Analysis
9. Product Analytics
10. Demand Forecast
11. Business Insights
12. CSV Data Explorer

## Dataset Information

Large original datasets are excluded from Git tracking. Required source datasets must be placed in the appropriate data directory before running the processing workflow.

## Project Status

Core analytics modules and the interactive dashboard are implemented. Testing, documentation, and deployment improvements are ongoing.

## Author

**Shekhar Shelke**

- GitHub: https://github.com/shekharshelke171-eng
- LinkedIn: https://www.linkedin.com/in/shekhar-shelke-6936263a6/
- Portfolio: https://portfolio-y7l1.vercel.app/

## 🐳 Docker Deployment

RetailPulse is successfully containerized using Docker.

### Docker Details

| Configuration | Value |
|---|---|
| Docker Image | `retailpulse-app:latest` |
| Container Name | `retailpulse-container` |
| Application Port | `8501` |
| Local URL | http://localhost:8501 |

### Build Docker Image

```bash
docker build -t retailpulse-app .
```

### Run Docker Container

```bash
docker run -d --name retailpulse-container -p 8501:8501 retailpulse-app
```

### Access Dashboard

Open your browser and visit:

http://localhost:8501

### Docker Testing Status

- Docker image built successfully.
- Container started successfully.
- Streamlit dashboard tested successfully in the browser.
- Dashboard pages and visualizations verified.

**Status:** Docker containerization and local testing completed successfully.
## ☸️ Kubernetes Deployment

RetailPulse was successfully deployed and tested locally using Kubernetes through Docker Desktop.

### Kubernetes Configuration

| Configuration | Value |
|---|---|
| Cluster Node | `desktop-control-plane` |
| Kubernetes Version | `v1.36.1` |
| Deployment | `retailpulse-deployment` |
| Pod Status | Running (1/1 Ready) |
| Service | `retailpulse-service` |
| Service Type | NodePort |
| Application Port | `8501` |
| NodePort | `30085` |

### Kubernetes Files

- `k8s/deployment.yaml` – Defines the RetailPulse application deployment.
- `k8s/service.yaml` – Configures network access to the application.

### Deployment Commands

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get nodes
kubectl get pods
kubectl get services
```

### Access the Dashboard

The application was successfully tested using Kubernetes port forwarding:

```bash
kubectl port-forward service/retailpulse-service 8502:8501
```

Open: http://localhost:8502

### Testing Results

- Kubernetes cluster started successfully.
- Kubernetes node reached Ready status.
- Application Pod reached Running status with 1/1 Ready.
- Kubernetes Service was created successfully.
- Streamlit dashboard was accessed and tested through port forwarding.

**Status:** Local Kubernetes deployment and dashboard testing completed successfully. This does not represent a production cloud deployment.