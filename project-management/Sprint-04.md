# Sprint-04 Development Task Board

This document tracks the task breakdowns, timelines, and execution objectives across the 4 weeks of **Sprint-04**.

---

## Week 1: Backend Foundation & Access Control
- **Objectives**: Initialize backend microservices, establish MongoDB connections, and implement authentication.
- **Tasks**:
  1. [ ] Devam: Initialize the main Express API backend service under `backend/`.
  2. [ ] Devam: Deploy MongoDB locally and verify connections using `docker-compose` configuration under `infrastructure/docker/`.
  3. [ ] Kalpesh: Implement admin registration and database entry schema.
  4. [ ] Kalpesh: Develop the Elliptic Curve Cryptography (ECC) challenge generation and signature validation logic.
  5. [ ] Kalpesh: Configure the JSON Web Token (JWT) session generation, token signing, and security validation middleware.
- **Deliverables**: Express core API, dockerized MongoDB stack, and ECC signature authentication pipeline.

---

## Week 2: Observability & Telemetry Scrapers
- **Objectives**: Configure metrics collection agents and database timeseries logging.
- **Tasks**:
  1. [ ] Devam: Deploy Node Exporter on the cluster host to capture system stats.
  2. [ ] Devam: Deploy and configure the Prometheus server to scrape cAdvisor and Node Exporter metrics.
  3. [ ] Devam: Create timeseries metric ingestion REST APIs in the Express backend.
  4. [ ] Kalpesh: Setup Grafana charts mapped to cluster Prometheus logs.
- **Deliverables**: Prometheus config maps, active Prometheus scraper, and timeseries backend router.

---

## Week 3: AI Analytics Core & Risk Scoring
- **Objectives**: Implement feature preprocessing, model classification, and risk calculation.
- **Tasks**:
  1. [ ] Dil: Build the Python preprocessing script (Min-Max Scaling, PCA reduction).
  2. [ ] Dil: Implement the unsupervised PyTorch Autoencoder model structure under `ai-engine/`.
  3. [ ] Dil: Build the Scikit-learn Isolation Forest classifier backup class.
  4. [ ] Dil: Write the model evaluation endpoint to compute reconstruction losses.
  5. [ ] Dil: Implement the Unified Risk Score (URS) calculation using anomaly scores and host weights.
- **Deliverables**: Python PCA scaler class, PyTorch Autoencoder model, URS generator API route.

---

## Week 4: Security Automation & Dashboard UI
- **Objectives**: Integrate the active remediation PEP loop and visual dashboard UI.
- **Tasks**:
  1. [ ] Devam: Write Ansible plays to dynamically alter node firewall parameters.
  2. [ ] Devam: Write shell-level Kubernetes triggers to update NetworkPolicies and label anomalous pods.
  3. [ ] Devam: Configure the Express WebSocket server to stream real-time ThreatEvents to client portals.
  4. [ ] Devam: Build the React Dashboard layout showing cluster log tables and active alert triggers.
  5. [ ] Shivraj: Execute simulated DDoS attacks to verify the entire telemetry-to-isolation workflow.
- **Deliverables**: Ansible plays, Kubernetes containment triggers, React Dashboard UI, and attack simulation reports.
