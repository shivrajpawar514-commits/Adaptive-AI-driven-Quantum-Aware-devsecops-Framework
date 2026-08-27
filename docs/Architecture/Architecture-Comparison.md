# Architecture Comparison: V1 vs. V2

This document evaluates the design changes introduced in Architecture-V2, comparing it with the V1 baseline, and validating its alignment with our research goals.

---

## 1. Architectural Changes (V1 vs. V2)

| Dimension | Architecture-V1 (Sprint-02) | Architecture-V2 (Sprint-03) |
| :--- | :--- | :--- |
| **Telemetry Ingestion** | Prometheus + eBPF raw streams. | Prometheus + Node Exporter + Local PCA Feature Engineering. |
| **AI Anomaly Detection** | Centralized heavy Deep Autoencoder. | Unsupervised Autoencoder or Isolation Forest (Lightweight). |
| **Risk Scoring** | Metric-level anomaly thresholds. | Unified Risk Score (URS) with Asset Criticality weights. |
| **Explainability** | Local LLM RAG sidecar (Mandatory). | Removed LLM from core path (Optional future scope). |
| **Quantum Module** | Simulation of QML Autoencoders on network logs. | Qiskit Bloch Sphere simulations + PQC migration study. |
| **Mitigation & Automation** | Kubernetes/Ansible/Terraform orchestration. | Concrete translation of risk to K8s/Ansible triggers (PEP). |
| **Database** | Timeseries logging files. | MongoDB structured collections. |

---

## 2. Rationale: Why V2 is Better

### 2.1. Removed Components
- **Mandatory Large Language Models (LLMs)**: LLMs were removed from the critical runtime flow. Running LLMs on container hosts introduces high memory/CPU usage, making the framework impractical for real-time edge or runner deployments (evidence from P02). LLMs are now listed as optional future integrations for offline ticket logging.
- **Production-Level QML Anomaly Detection**: Replaced real-time QML network scanners with simulator-based validation and cryptographic study. Production QML is currently simulator-bound due to NISQ qubit limits (evidence from P10).

### 2.2. Simplified Components
- **Telemetry Processing**: Replaced raw, high-dimensional packet scrapes with a localized **Feature Engineering (PCA)** pipeline. Dimensionality reduction cuts model classification latency by up to 40% (evidence from P09).
- **Lightweight AI**: Focused exclusively on unsupervised Autoencoders and Isolation Forests. These models require minimal CPU/GPU overhead compared to spatial-temporal models (CNN-LSTMs) and are highly feasible for container sidecars.

### 2.3. Research Gaps Addressed
- **The Performance Overhead Gap**: V2 addresses the latency trade-off (gap from P07, P09) by standardizing on low-overhead models and PCA feature reduction.
- **The Policy Translation Gap**: V2 details a concrete PEP-PDP workflow where Risk Scores (calculated dynamically) drive Kubernetes NetworkPolicies and Ansible reconfigurations automatically (gap from P05, P08).

### 2.4. Future Work Remaining
- **Multi-Cloud Policy Synchronization**: Translating isolation decisions across multiple cloud gateways (AWS/GCP) dynamically.
- **Physical Quantum hardware migration**: Transitioning the Qiskit simulators to actual NISQ processors as physical error rates decrease.
