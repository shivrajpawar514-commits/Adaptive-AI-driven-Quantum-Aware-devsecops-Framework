# Project Scope Document

This document defines the functional boundaries, technology selections, and scope limitations of the Adaptive AI-Driven DevSecOps Framework.

---

## 1. IN SCOPE

### 1.1. Core Capabilities
- **Cloud Monitoring**: Scrapes system, node, and container telemetry metrics using **Prometheus** and **Node Exporter**.
- **AI Threat Detection**: Executes unsupervised anomaly detection on resource and network telemetry using **Autoencoders** or **Isolation Forests**.
- **Risk Scoring**: Formulates a Unified Risk Score (URS, 0-100) combining anomaly loss with static host criticality context.
- **DevSecOps Automation**: Automates threat containment (PEP execution layer) using shell commands, **Ansible** playbooks, and **Kubernetes** custom NetworkPolicies.
- **Client Access Layer**: Implements administrative authentication via Elliptic Curve Cryptography (**ECC**) signature verification.
- **Visualization Interface**: Renders real-time telemetry, risk scores, and alert logs on a React-based **Security Dashboard**.
- **Quantum Simulation**: Simulates post-quantum algorithms and qubit behaviors using a **Bloch Sphere Simulator** and **Qiskit** scripting.
- **Migration Planning**: Evaluates post-quantum container transition pathways and benchmarks.

### 1.2. Technology Stack
- **Container Host**: Docker, Kubernetes (local Kind/Minikube environment).
- **IaC & Automation**: Terraform, Ansible.
- **Databases**: MongoDB (document logging store).
- **Backend API**: Node.js (Express).
- **Frontend UI**: React.

---

## 2. OUT OF SCOPE

- **Building New Cryptographic Algorithms**: The project integrates existing post-quantum libraries (NIST PQC standards via liboqs or OpenSSL providers) rather than creating new cryptosystems.
- **Training Large Language Models (LLMs)**: LLMs are excluded from the runtime pipeline to minimize node resource overhead.
- **Deploying on Physical Quantum Hardware**: The project relies exclusively on classical quantum simulators (Qiskit) for Bloch Sphere modeling.
- **Inventing New AI Algorithms**: Utilizes standard PyTorch Autoencoders and Scikit-learn Isolation Forests.
- **High-Throughput Production Deployment**: Focuses on validation testbeds rather than enterprise production scaling.
- **Multi-Region Cloud Deployment**: Telemetry collection and isolation loops are implemented inside a single Kubernetes cluster namespace.
