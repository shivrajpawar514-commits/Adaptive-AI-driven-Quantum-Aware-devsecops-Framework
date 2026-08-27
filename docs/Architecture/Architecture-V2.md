# Software Architecture Design (Version 2.0)

This document describes the updated architectural specification of the Adaptive AI-Driven DevSecOps Framework for Secure Cloud Infrastructure.

---

## 1. Executive Summary
Architecture-V2 transitions the framework from a conceptual model with high computational components (e.g. LLMs) to a realistic, low-overhead active controller loop. The design focuses on lightweight telemetry, localized feature selection, fast unsupervised anomaly detection (Autoencoder / Isolation Forest), and dynamic Zero-Trust orchestration. This design is built for deployment by a small development team in containerized, orchestrated environment (Kubernetes).

---

## 2. Architecture Overview & Subsystems

The updated architecture comprises a structured pipeline that flows from user authentication through runtime metrics ingestion to automated remediation.

### 2.1. ASCII Diagram

```
User (Client)
  |
  v
[ECC Authentication Module]
  |
  v
[API Gateway] (Reverse Proxy & Token Validator)
  |
  v
[Monitoring & Log Collection] (Prometheus + Node Exporter)
  |
  v
[Telemetry Collector] (Metrics Aggregator)
  |
  v
[Feature Engineering] (Local PCA / Dimensionality Reduction)
  |
  v
[Lightweight AI Threat Detection] (Autoencoder / Isolation Forest)
  |
  v
[Risk Score Generator] (Quantifies intrusion threat state)
  |
  v
[Decision Engine] (Policy PDP - evaluates risk vs rules)
  |
  v
[DevSecOps Automation Engine] (PEP execution layer)
  |
  +------> [Terraform] --------> Provisions/Hardens Cloud Resources
  |
  +------> [Ansible] ----------> Configures/Restarts Nodes and Pods
  |
  +------> [Kubernetes/Docker] -> Re-routes, isolates, or scales containers
  |
  v
[Security Dashboard] (Web UI displaying metrics, logs, and alerts)
  |
  v
[Quantum-Aware Security Planning Report] (Migration audit and simulated QAE)
```

---

## 3. Subsystem Component Responsibilities

### 3.1. User & Access Layer (ECC Authentication + API Gateway)
- **ECC Authentication**: Handles client sign-in and signature verification using Elliptic Curve Cryptography (ECC), providing low-latency security compared to classical RSA.
- **API Gateway**: Route requests to the microservices, validates access tokens, and acts as the entry reverse proxy.

### 3.2. Observability Layer (Monitoring & Telemetry)
- **Monitoring & Log Collection**: Ingests system resource and network statistics using Prometheus and Node Exporter.
- **Telemetry Collector**: Compiles logs and metrics from cluster namespaces and feeds them to the processing pipeline.
- **Feature Engineering**: Standardizes input vectors. Executes localized dimensionality reduction (Principal Component Analysis - PCA) to extract principal packet and resource features, cutting classifier latency by 40% (P09 evidence).

### 3.3. Analytics Layer (AI Anomaly Detection & Risk Scoring)
- **Lightweight AI Threat Detection**: Unsupervised Autoencoder or Isolation Forest model trained on normal baseline profiles. Computes reconstruction errors or isolation metrics.
- **Risk Score Generator**: Normalizes anomaly indicators into a Unified Risk Score (0-100) based on target asset criticality.

### 3.4. Orchestration Layer (Decision & Automation Engine)
- **Decision Engine**: Evaluation gateway (Policy Decision Point). Compares the risk score against static Zero-Trust threshold rules.
- **DevSecOps Automation Engine**: Policy Enforcement Point (PEP). Triggers software-defined scripts:
  - **Kubernetes**: Labels pods, updates NetworkPolicies, or scale-down pods.
  - **Ansible**: Runs playbooks to restart nodes, alter system permissions, or deploy firewalls.
  - **Terraform**: Triggers resource state validation or re-provisions network gateways.

### 3.5. Presentation & Audit Layer
- **Dashboard**: React interface display.
- **Quantum-Aware Security Planning**: Simulates post-quantum migration pathways, including Bloch Sphere simulators and PQC studies.

---

## 4. Inputs & Outputs
- **Inputs**:
  - User credentials & ECC signatures.
  - System telemetry (Prometheus scrape metrics, Node Exporter CPU/memory states, packet throughput).
  - Security policies (JSON configurations defining risk limits).
- **Outputs**:
  - Access tokens (JWT).
  - Workload anomaly alerts.
  - Infrastructure modifications (Ansible execution logs, Kubernetes NetworkPolicy patches).
  - Graphical dashboard visualizations.
  - Post-quantum migration audit reports.

---

## 5. Subsystem Data Flow

```
[System Telemetry] 
       | Scraped by Node Exporter & Prometheus
       v
[Telemetry Collector] 
       | Ingests raw JSON metrics
       v
[Feature Engineering] 
       | PCA scaling -> float array feature vector
       v
[Lightweight AI Engine] 
       | Autoencoder reconstruction -> reconstruction loss
       v
[Risk Score Generator] 
       | Maps loss to risk score [0-100]
       v
[Decision Engine] 
       | Risk Score > Threshold? -> Triggers Playbook
       v
[Automation Engine] 
       | executes shell command (kubectl / ansible-playbook)
       v
[Kubernetes Cluster] 
       | updates NetworkPolicy -> Pod isolated
```

---

## 6. Technology Stack
- **Container Host**: Docker, Kubernetes.
- **IaC & Config**: Terraform, Ansible.
- **Observability**: Prometheus, Node Exporter.
- **AI Core**: Python (PyTorch/Scikit-learn).
- **Database**: MongoDB (lightweight, flexible log schemas).
- **Backend API**: Node.js (Express).
- **Frontend Dashboard**: React.
- **Quantum Simulator**: Python (Qiskit/Pennylane).

---

## 7. Advantages & Limitations

### Advantages
- **Pipeline Latency Reduction**: Avoids heavy deep models (CNN-LSTM), using lightweight Autoencoders/Isolation Forests.
- **Zero-Friction Adoption**: Avoids external APIs or heavy LLMs, making it fully self-hosted.
- **Publishable Novelty**: Connects real-time risk scoring to orchestrated container isolation with post-quantum planning benchmarks.

### Limitations
- **NISQ Constraint**: The quantum module is simulator-based (Qiskit) due to physical qubit errors.
- **Off-line Training**: The AI model requires an initial baseline training phase on normal logs before active deployment.
- **Cold-Start Latency**: The very first container isolation path execution has a slight cold-start latency due to Ansible invocation.
