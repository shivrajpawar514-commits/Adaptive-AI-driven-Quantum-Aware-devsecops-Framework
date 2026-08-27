# Installation & Deployment Guide

This guide details instructions for setting up the local DevSecOps SOAR framework.

---

## 1. Prerequisites
- Python 3.11+
- MongoDB 6.0+ (Local or Atlas instance)
- Docker & Docker Compose (Optional, for microservices orchestration)

---

## 2. Local Setup Steps
1. Clone the repository.
2. Initialize virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env`.
5. Start the Automation Engine API:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```
