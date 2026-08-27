# System Module Specifications

This document defines the purpose, responsibilities, input/output structures, technology stacks, and future improvement paths for the framework's core modules.

---

## 1. Authentication Module
- **Purpose**: Secures administrative access using low-latency, post-quantum transition cryptography.
- **Responsibilities**: Generates nonces, validates client sign-in challenges using Elliptic Curve Cryptography (ECC) public keys, and issues JWT session tokens.
- **Inputs**: Authentication signature, username, and challenge nonce.
- **Outputs**: Signed JWT token, status response.
- **Technologies**: Node.js, `elliptic` library, JSON Web Tokens (JWT).
- **Future Improvements**: Integrating hybrid ECC-Dilithium key verification as post-quantum libraries (liboqs) reach production standards.

---

## 2. Monitoring Module
- **Purpose**: Collects system metrics and container resource telemetry.
- **Responsibilities**: Scrapes pod CPU/memory and virtual network switches. Logs cluster operations.
- **Inputs**: Container host events, socket stream packet flows.
- **Outputs**: Telemetry metrics (raw JSON), Prometheus scrape targets.
- **Technologies**: Prometheus, Node Exporter, cAdvisor.
- **Future Improvements**: Transitioning log scraping to lightweight eBPF kernel agents to minimize execution overhead.

---

## 3. AI Module
- **Purpose**: Detects microservice network anomalies using lightweight, self-hosted AI models.
- **Responsibilities**: Standardizes metrics vectors, reduces features using PCA, executes unsupervised reconstruction evaluations, and calculates anomaly losses.
- **Inputs**: Telemetry logs (float arrays).
- **Outputs**: Reconstruction loss, anomaly classification flag (Boolean).
- **Technologies**: Python (PyTorch, Scikit-learn), Pandas.
- **Future Improvements**: Implementing online incremental learning to update model baselines without complete retraining.

---

## 4. Risk Engine
- **Purpose**: Translates raw anomaly scores into a standardized risk index.
- **Responsibilities**: Evaluates reconstruction losses against thresholds and applies host/asset criticality weights.
- **Inputs**: Reconstruction loss, context metadata (source port, target asset).
- **Outputs**: Unified Risk Score (URS, 0-100).
- **Technologies**: Python, MongoDB.
- **Future Improvements**: Integrating dynamic context parameters (e.g. active time-of-day access baselines).

---

## 5. Decision Engine
- **Purpose**: Directs the mitigation workflow based on active security rules (Policy Decision Point).
- **Responsibilities**: Evaluates risk scores against Zero-Trust policies. Checks validation states.
- **Inputs**: Unified Risk Score (URS), JSON Policy definition.
- **Outputs**: Automation trigger instructions.
- **Technologies**: Node.js, Open Policy Agent (OPA).
- **Future Improvements**: Integrating compliance checks (GDPR/PCI-DSS) into the decision rules database.

---

## 6. Automation Engine
- **Purpose**: Executes software-defined security changes (Policy Enforcement Point).
- **Responsibilities**: Triggers container network isolation, restarts nodes, or re-provisions network gateways.
- **Inputs**: Trigger instructions (Kubernetes pod ID, target actions).
- **Outputs**: Shell outputs, Ansible/Terraform runtime logs, container state changes.
- **Technologies**: Kubernetes CLI (`kubectl`), Ansible playbooks, Terraform runner.
- **Future Improvements**: Building multi-cloud automated policy routing for unified GCP/AWS security group changes.

---

## 7. Dashboard
- **Purpose**: Visualizes cluster health, threat events, and system performance.
- **Responsibilities**: Displays real-time risk scores, alerts, and node connection states.
- **Inputs**: REST API responses, WebSocket telemetry streams.
- **Outputs**: Graphical React components, sound/visual alert triggers.
- **Technologies**: React, TailwindCSS, Chart.js, WebSockets.
- **Future Improvements**: Interactive network topology diagrams showing live isolated pods.

---

## 8. Quantum Module
- **Purpose**: Simulates quantum key behaviors and designs future migration plans.
- **Responsibilities**: Models qubit states on Bloch Spheres, evaluates PQC library connection stats, and outlines post-quantum hardware transition plans.
- **Inputs**: Classical network log samples.
- **Outputs**: Simulator output vectors, migration audit reports.
- **Technologies**: Python (Qiskit/Pennylane).
- **Future Improvements**: Testing parameterized quantum circuits on actual IBM quantum nodes.
