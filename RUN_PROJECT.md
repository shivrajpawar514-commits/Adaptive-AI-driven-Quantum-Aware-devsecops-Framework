# DevSecOps Framework — Complete Local Execution & Operations Guide

This guide provides step-by-step instructions to run the entire DevSecOps framework locally without Docker.

---

## 1. Quick Start Summary

### Dashboard Execution (Frontend)
```bash
# Correct directory is 'dashboard' (NOT 'frontend')
cd dashboard
npm install
npm run dev
```
**Local URL**: `http://localhost:5173`

---

## 2. Execution Order & Service Matrix

Run the services in the following recommended startup sequence:

| Step | Microservice | Directory | Startup Command | Local Port | Health Check URL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Backend Gateway** | `./backend` | `npm start` | `5000` | `http://localhost:5000/health` |
| **2** | **Monitoring Service** | `./monitoring-service` | `npm start` | `6001` | `http://localhost:6001/health` |
| **3** | **AI Engine** | `./ai-engine` | `uvicorn src.api.main:app --port 8000` | `8000` | `http://localhost:8000/health` |
| **4** | **Cloud Adapter** | `./cloud-adapter` | `uvicorn src.main:app --port 7000` | `7000` | `http://localhost:7000/health` |
| **5** | **Risk Engine** | `./risk-engine` | `uvicorn src.api.main:app --port 8500` | `8500` | `http://localhost:8500/health` |
| **6** | **Attack Simulator** | `./attack-simulator` | `uvicorn src.main:app --port 8600` | `8600` | `http://localhost:8600/health` |
| **7** | **Policy Engine** | `./policy-engine` | `uvicorn src.main:app --port 8700` | `8700` | `http://localhost:8700/health` |
| **8** | **Research Evaluator** | `./research-evaluator` | `uvicorn src.main:app --port 8800` | `8800` | `http://localhost:8800/health` |
| **9** | **Digital Twin** | `./digital-twin` | `uvicorn src.main:app --port 8900` | `8900` | `http://localhost:8900/health` |
| **10** | **Report Generator** | `./report-generator` | `uvicorn src.main:app --port 9000` | `9000` | `http://localhost:9000/health` |
| **11** | **Dashboard UI** | `./dashboard` | `npm run dev` | `5173` | `http://localhost:5173` |

---

## 3. Detailed Microservice Startup Commands

### 1. Backend Gateway (Port 5000)
```bash
cd backend
npm install
npm start
```
- **Dependencies**: Node.js, Express, MongoDB
- **Expected Log**: `Server is running on port 5000`

### 2. Monitoring Service (Port 6001)
```bash
cd monitoring-service
npm install
npm start
```
- **Dependencies**: Node.js, Express, systeminformation
- **Expected Log**: `Monitoring service running on port 6001`

### 3. AI Anomaly Engine (Port 8000)
```bash
cd ai-engine
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```
- **Dependencies**: Python 3.10+, FastAPI, PyTorch, Scikit-learn
- **Expected Log**: `Uvicorn running on http://0.0.0.0:8000`

### 4. Cloud Adapter (Port 7000)
```bash
cd cloud-adapter
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 7000
```
- **Dependencies**: Python 3.10+, FastAPI, Boto3 SDK
- **Expected Log**: `Uvicorn running on http://0.0.0.0:7000`

### 5. Adaptive Risk Engine (Port 8500)
```bash
cd risk-engine
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8500
```
- **Dependencies**: Python 3.10+, FastAPI, NumPy
- **Expected Log**: `Uvicorn running on http://0.0.0.0:8500`

### 6. Attack Simulator (Port 8600)
```bash
cd attack-simulator
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8600
```
- **Dependencies**: Python 3.10+, FastAPI, HTTPX
- **Expected Log**: `Uvicorn running on http://0.0.0.0:8600`

### 7. Policy Recommendation Engine (Port 8700)
```bash
cd policy-engine
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8700
```
- **Dependencies**: Python 3.10+, FastAPI, Pydantic
- **Expected Log**: `Uvicorn running on http://0.0.0.0:8700`

### 8. Research Evaluator Framework (Port 8800)
```bash
cd research-evaluator
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8800
```
- **Dependencies**: Python 3.10+, FastAPI, SciPy
- **Expected Log**: `Uvicorn running on http://0.0.0.0:8800`

### 9. Digital Twin Service (Port 8900)
```bash
cd digital-twin
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8900
```
- **Dependencies**: Python 3.10+, FastAPI, NetworkX
- **Expected Log**: `Uvicorn running on http://0.0.0.0:8900`

### 10. Autonomous Report Generator (Port 9000)
```bash
cd report-generator
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 9000
```
- **Dependencies**: Python 3.10+, FastAPI, Jinja2
- **Expected Log**: `Uvicorn running on http://0.0.0.0:9000`

---

## 4. API & Data Flow Routing Matrix

| Dashboard Feature | API Endpoint | Microservice Port | Target Mongo Collection |
| :--- | :--- | :--- | :--- |
| **System Telemetry Cards** | `GET /api/metrics` | Monitoring Service (`6001`) | `metrics` |
| **Orchestrator Health** | `GET /system/status` | Backend Gateway (`5000`) | N/A |
| **AI Anomaly Inference** | `POST /predict` | AI Engine (`8000`) | `predictions` |
| **Adaptive URS Risk Score** | `POST /risk/evaluate` | Risk Engine (`8500`) | `risk_results` |
| **Quantum Readiness** | `POST /risk/evaluate` | Risk Engine (`8500`) | `risk_results` |
| **Policy Playbooks** | `POST /policy/recommend` | Policy Engine (`8700`) | `recommendations` |
| **Attack Simulation** | `POST /simulation/run` | Attack Simulator (`8600`) | `attack_simulations` |
| **Cloud Discovery** | `GET /cloud/assets` | Cloud Adapter (`7000`) | `cloud_assets` |
| **Digital Twin Topology** | `GET /digital-twin/graph` | Digital Twin (`8900`) | N/A |
| **Benchmarking KPIs** | `GET /evaluation/dashboard` | Research Evaluator (`8800`) | `research_evaluations` |
| **Generated Reports** | `GET /report/latest` | Report Generator (`9000`) | `reports` |

---

## 5. Troubleshooting & FAQ

### Issue: `ENOENT: Could not read package.json` when running `cd frontend`
- **Cause**: The web application frontend is located in `./dashboard`, NOT `./frontend`.
- **Solution**: Run `cd dashboard` instead of `cd frontend`.

### Issue: MongoDB connection error on service startup
- **Cause**: Local MongoDB daemon is not running or `MONGO_URI` environment variable is not configured.
- **Solution**: Services automatically fall back to high-fidelity simulated/in-memory mode if MongoDB is unavailable. To connect to MongoDB, ensure `MONGO_URI` is set in `.env`.
