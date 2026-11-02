\# RetailPulse - Installation Guide



\## 1. Project Overview



RetailPulse is an AI-powered customer analytics and demand forecasting platform built using Python and Streamlit.



\## 2. Prerequisites



\- Python 3.10 or compatible version

\- pip package manager

\- Git (optional)



\## 3. Project Setup



Clone or download the RetailPulse project repository.



Open PowerShell or Command Prompt in the project root directory.



\## 4. Create Virtual Environment



```bash

python -m venv venv

## Docker Deployment and Testing

The RetailPulse application was successfully containerized using Docker.

### Docker Configuration

- **Docker Image:** `retailpulse-app:latest`
- **Container Name:** `retailpulse-container`
- **Application Port:** `8501`
- **Local URL:** http://localhost:8501

### Testing Results

- Docker image was built successfully.
- Docker container started successfully.
- Streamlit dashboard was accessible through the local browser.
- Dashboard pages, charts, and data were tested successfully.

**Status:** Docker containerization and local application testing completed successfully.

## Kubernetes Deployment

RetailPulse was successfully deployed and tested locally using Kubernetes through Docker Desktop.

### Kubernetes Configuration

| Configuration | Value |
|---|---|
| Cluster Node | desktop-control-plane |
| Kubernetes Version | v1.36.1 |
| Deployment | retailpulse-deployment |
| Pod Status | Running (1/1 Ready) |
| Service | retailpulse-service |
| Service Type | NodePort |
| Application Port | 8501 |
| NodePort | 30085 |

### Deployment Commands

Apply Deployment:

```bash
kubectl apply -f k8s/deployment.yaml