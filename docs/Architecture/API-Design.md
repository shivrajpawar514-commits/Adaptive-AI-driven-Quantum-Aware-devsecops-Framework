# API Design Specification (REST API Endpoints)

This document details the REST API specifications for authentication, threat detection, monitoring, automation, dashboard analytics, and research results.

---

## 1. Authentication Endpoints

### 1.1. POST /login
- **Purpose**: Authenticates system administrators using ECC-based challenge-response signature verification.
- **Request Body**:
  ```json
  {
    "username": "admin1",
    "signature": "MEQCIFz/2V...",
    "challenge": "8a3d4f..."
  }
  ```
- **Response**:
  - **Success (200 OK)**:
    ```json
    {
      "status": "success",
      "token": "eyJhbGciOi..."
    }
    ```
- **Validation**: `username` must be alphanumeric. `signature` must be a valid hex-encoded string. `challenge` must match the recently issued nonce.
- **Security**: Validates signature using client's registered ECC public key. Implements request throttling to prevent brute-force attacks.

### 1.2. POST /register
- **Purpose**: Registers a new administrator with public keys.
- **Request Body**:
  ```json
  {
    "username": "admin2",
    "email": "admin2@university.edu",
    "password": "StrongPassword123!",
    "ecc_public_key": "-----BEGIN PUBLIC KEY-----\n..."
  }
  ```
- **Response**:
  - **Success (201 Created)**:
    ```json
    {
      "status": "created",
      "user_id": "60d5ec..."
    }
    ```
- **Validation**: Email validation. Password strength limits (min 12 chars, digits, uppercase, special). Public key format check.
- **Security**: Password hashed using Argon2id. Encrypted transmission over TLS.

### 1.3. POST /logout
- **Purpose**: Invalidates the admin's session token.
- **Request Headers**: `Authorization: Bearer <token>`
- **Response**:
  - **Success (200 OK)**:
    ```json
    {
      "status": "logged_out"
    }
    ```
- **Validation**: Requires active Bearer token.
- **Security**: Revokes the JWT by adding it to a Redis blacklist database.

---

## 2. Threat Detection Endpoints

### 2.1. POST /predict
- **Purpose**: Ingests preprocessed network packet metrics and outputs anomaly classification.
- **Request Body**:
  ```json
  {
    "pod_id": "pod-874f",
    "features": [0.12, 1.45, 0.0, 120.4, 0.05, 12.1]
  }
  ```
- **Response**:
  - **Success (200 OK)**:
    ```json
    {
      "pod_id": "pod-874f",
      "reconstruction_loss": 0.045,
      "anomaly_detected": true
    }
    ```
- **Validation**: `features` must be an array of floats matching model's expected dimension.
- **Security**: Internal endpoint. Restrict access using mutual TLS (mTLS) to telemetry collector pods only.

### 2.2. POST /risk-score
- **Purpose**: Evaluates anomaly loss and outputs risk scores.
- **Request Body**:
  ```json
  {
    "pod_id": "pod-874f",
    "reconstruction_loss": 0.045,
    "context": {
      "port": 80,
      "source_ip": "10.244.0.12"
    }
  }
  ```
- **Response**:
  - **Success (200 OK)**:
    ```json
    {
      "pod_id": "pod-874f",
      "risk_score": 88,
      "action_required": true
    }
    ```
- **Validation**: `reconstruction_loss` must be positive.
- **Security**: Internal only. Rate-limited.

---

## 3. Monitoring Endpoints

### 3.1. GET /metrics
- **Purpose**: Fetches runtime Prometheus timeseries stats for the dashboard.
- **Query Params**: `pod_id`, `range` (e.g. `1h`)
- **Response (200 OK)**:
  ```json
  [
    { "timestamp": "2026-07-07T14:00:00Z", "cpu": 12.5, "memory": 204.8 }
  ]
  ```
- **Security**: Requires admin authentication token.

### 3.2. GET /logs
- **Purpose**: Retrieves cluster security logs.
- **Query Params**: `limit`, `status`
- **Response (200 OK)**: List of log records.
- **Security**: JWT Authentication. Role-based check (only `admin` and `auditor`).

### 3.3. GET /alerts
- **Purpose**: Retrieves unresolved threat events.
- **Response (200 OK)**: List of alerts.
- **Security**: JWT Authentication.

---

## 4. Automation Endpoints

### 4.1. POST /response
- **Purpose**: Incurs dynamic container actions.
- **Request Body**:
  ```json
  {
    "threat_id": "60d5fc...",
    "action": "isolate"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "mitigation_initiated",
    "latency_ms": 12.4
  }
  ```
- **Security**: Admin token. mTLS for Kubernetes API triggers.

### 4.2. POST /block
- **Purpose**: Triggers Ansible/Kubernetes firewall block on IP.
- **Request Body**:
  ```json
  { "ip_to_block": "192.168.1.105" }
  ```
- **Response (200 OK)**: success status.
- **Security**: High-privilege admin only.

### 4.3. POST /restart
- **Purpose**: Restarts a compromised namespace or pod.
- **Request Body**:
  ```json
  { "pod_id": "pod-874f" }
  ```
- **Response (200 OK)**: success status.
- **Security**: High-privilege admin only.

### 4.4. POST /policy
- **Purpose**: Modifies the risk thresholds of active Zero-Trust rules.
- **Request Body**:
  ```json
  {
    "policy_name": "Strict Pod Isolation",
    "risk_threshold": 75
  }
  ```
- **Response (200 OK)**: updated policy status.
- **Security**: Admin authentication. Changes audited in `SecurityLogs`.

---

## 5. Dashboard Endpoint

### 5.1. GET /dashboard
- **Purpose**: Fetches critical telemetry summary.
- **Response (200 OK)**:
  ```json
  {
    "total_threats_blocked": 14,
    "current_risk_status": "Low",
    "avg_response_latency_ms": 112.4,
    "active_pods": 8
  }
  ```
- **Security**: JWT Authentication.

---

## 6. Research & Experiments Endpoints

### 6.1. GET /experiments
- **Purpose**: Returns parameters of research evaluation tests.
- **Response (200 OK)**: List of experiments.
- **Security**: Public read for transparency; write requires admin token.

### 6.2. GET /results
- **Purpose**: Fetches raw data values for statistical validation.
- **Response (200 OK)**: Excel/JSON list of run records.
- **Security**: Public read for publication reproducibility.
