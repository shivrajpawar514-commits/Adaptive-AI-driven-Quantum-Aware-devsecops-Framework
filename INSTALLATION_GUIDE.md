# Installation & Deployment Guide

This guide details instructions for setting up and running the DevSecOps SOAR framework from a clean checkout.

---

## 1. Prerequisites
- **Python**: 3.11+
- **Git**
- **MongoDB 6.0+** (Optional: falls back to built-in in-memory Mock Database if MongoDB is not present)
- **Docker & Docker Compose** (Optional: for full multi-container microservice orchestration)

---

## 2. Clean Checkout Setup Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/shivrajpawar514-commits/Adaptive-AI-driven-Quantum-Aware-devsecops-Framework.git
cd Adaptive-AI-driven-Quantum-Aware-devsecops-Framework
```

### Step 2: Initialize Virtual Environment
```bash
python3 -m venv venv

# On Linux / macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
The root `requirements.txt` contains all core dependencies for the optimization engine, API services, benchmarks, and testing suites:
```bash
pip install -r requirements.txt
```

### Step 4: Run the Test Suites
Verify that the core algorithm, cycle checks, tie-breakers, dry-run mode, and authorization controls pass:
```bash
# Run root unit tests:
pytest tests/unit -v

# Run automation engine tests:
cd automation-engine
PYTHONPATH=. pytest tests/ -v
cd ..
```

### Step 5: Run Reproducible Benchmarks
Benchmark the Deterministic Playbook Optimizer against the Naive Greedy Baseline over 1,000 iterations:
```bash
python scripts/benchmark_optimizer.py
```

### Step 6: Start the Automation Engine Service
Start the FastAPI Automation Engine service on port 9100:
```bash
cd automation-engine
uvicorn src.main:app --host 127.0.0.1 --port 9100 --reload
```
API Documentation will be interactively accessible at: `http://127.0.0.1:9100/docs`.
