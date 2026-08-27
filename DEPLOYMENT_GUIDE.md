# Deployment & Setup Guide: DevSecOps Framework

This guide explains how to install dependencies, configure environment files, and start all microservices and the frontend React dashboard.

## 1. Prerequisites
Ensure you have the following installed on your host system:
* **Node.js** (v18 or higher)
* **Python** (v3.10 or higher)
* **npm** (v9 or higher)
* **pip** (v22 or higher)

---

## 2. Environment Variables & MongoDB Atlas
Create/configure `.env` files in each service directory. All services are configured to share the same MongoDB Atlas cluster:

### Backend: `/backend/.env`
```
PORT=5000
NODE_ENV=development
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?appName=devsecops
JWT_SECRET=devsecops_jwt_secret_key
MONITORING_SERVICE_URL=http://localhost:6001
AI_ENGINE_URL=http://localhost:8000
RISK_ENGINE_URL=http://localhost:8500
```

### Monitoring: `/monitoring-service/.env`
```
PORT=6001
NODE_ENV=development
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?appName=devsecops
```

### AI Engine: `/ai-engine/.env`
```
PORT=8000
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?appName=devsecops
```

### Risk Engine: `/risk-engine/.env`
```
PORT=8500
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?appName=devsecops
```

---

## 3. Running Services Locally (Without Docker)

Open four separate terminals and run the following startup commands:

### Terminal 1: Backend Gateway
```bash
cd backend
npm install
npm start
```

### Terminal 2: Telemetry Ingestor
```bash
cd monitoring-service
npm install
npm start
```

### Terminal 3: AI Anomaly Engine
```bash
cd ai-engine
pip install -r requirements.txt
python -m uvicorn src.api.main:app --port 8000 --host 127.0.0.1
```

### Terminal 4: Risk Scoring Engine
```bash
cd risk-engine
pip install -r requirements.txt
python -m uvicorn src.api.main:app --port 8500 --host 127.0.0.1
```

---

## 4. Running with Docker Compose
If you prefer containerized deployment, run:
```bash
docker-compose up --build
```
This launches the MongoDB container locally alongside the microservices.

---

## 5. Starting the Dashboard
To start the React Tailwind CSS v4 dashboard UI:
```bash
cd dashboard
npm install
npm run dev
```
Open **[http://localhost:5173/](http://localhost:5173/)** to access the visualization panel.
