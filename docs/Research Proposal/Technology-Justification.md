# Technology Justification Report

This document justifies the selection of the core technologies, frameworks, and models utilized in our framework, referencing evidence from the analyzed literature (P01 - P10).

---

## 1. Cloud-Native & Orchestration Infrastructure

### 1.1. Docker & Kubernetes
- **Justification**: Modern cloud applications are built around containerized microservices. According to **Rajapakse et al. (P03)** and **Almulla et al. (P05)**, containerization (Docker) and orchestration (Kubernetes) are the dominant platforms for running secure, scalable, and isolated applications. Using Kubernetes allows us to enforce Zero-Trust micro-segmentation by dynamically applying NetworkPolicies to isolate compromised nodes.

### 1.2. Terraform & Ansible
- **Justification**: Infrastructure as Code (IaC) is highlighted as the primary solution to tool-configuration errors and deployment drift in **Rajapakse et al. (P03)** and **Fu et al. (P02)**. Terraform allows us to provision secure-by-default infrastructure configurations, while Ansible provides the lightweight, agentless automation required to dynamically run firewall rules or restart compromised nodes during runtime containment (evidence from **P08**).

---

## 2. Observability & Databases

### 2.1. Prometheus & Grafana
- **Justification**: Real-time telemetry is essential for anomaly detection. **Saleh et al. (P07)** and **Alzoubi et al. (P01)** note that continuous monitoring is a prerequisite for cloud threat detection. Prometheus provides lightweight metrics scraping from cAdvisor and Node Exporter with low overhead, while Grafana offers standard visualization endpoints.

### 2.2. MongoDB
- **Justification**: Threat logs and telemetry datasets are highly unstructured. According to DevSecOps surveys (e.g. **P02**), relational databases introduce schema rigidity that slows down continuous delivery. MongoDB provides the flexible, JSON-compatible storage required to log diverse system logs and experiment results without performance bottlenecks.

---

## 3. Programming & Frontend

### 3.1. Node.js & React
- **Justification**: **Binbeshr et al. (P06)** notes that DevSecOps agility requires fast, event-driven backends. Node.js provides a non-blocking I/O model suitable for coordinating telemetry streams and running automation shell commands. React is selected to build a modular, high-frequency dashboard using WebSockets to render alert notifications in real-time.

---

## 4. Modeling Core (AI & Cryptography)

### 4.1. Autoencoder & Isolation Forest
- **Justification**: Classical machine learning struggles with the high volume of cloud traffic, while deep models like CNN-LSTMs introduce high computational latency (evidence from **P07**, **P09**). Autoencoders and Isolation Forests are selected because they are lightweight, unsupervised models that can run in container sidecars with under 5% CPU overhead, while retaining high zero-day threat detection accuracy (evidence from **P01**, **P04**, **P08**).

### 4.2. Elliptic Curve Cryptography (ECC)
- **Justification**: Traditional authentication schemes (like RSA) introduce high cryptographic handshake latency, causing pipeline delays. **Rajapakse et al. (P03)** notes that low-overhead authentication is key to reducing security friction. ECC provides comparable security to RSA with significantly smaller key sizes and faster verification times.

---

## 5. Quantum Simulation Core

### 5.1. Qiskit & Bloch Sphere
- **Justification**: Physical post-quantum hardware is currently limited by qubit decoherence and gate errors, making production deployment impractical (evidence from **Corli et al., P10**). Qiskit and Bloch Sphere simulators allow the framework to model and validate quantum autoencoder anomaly detection and PQC key states on classical hardware, providing an implementable transition roadmap.
