# Research Novelty Tracker & Feasibility Report

This tracker analyzes the academic baseline of existing literature, identifies gaps, evaluates internship feasibility, and outlines our framework's core research contribution.

---

## 1. What Existing Papers Are Doing
- **Static Scanners in CI/CD**: Running SAST/DAST tools during builds to identify code vulnerabilities (P02, P03, P06).
- **Offline Anomaly Detection**: Training deep learning models (CNN-LSTM, RNN) on offline traffic datasets (CSE-CIC-IDS2018) and validating detection accuracy (P04, P07).
- **Conceptual Zero-Trust Frameworks**: Outlining security policies and theoretical threat-mitigation paths in multi-cloud architectures (P05).
- **Quantum Simulator Research**: Modeling unsupervised autoencoder anomaly detection on quantum simulators like Qiskit (P10).

---

## 2. What Existing Papers Are NOT Doing
- **Dynamic Policy Translation**: Translating high-reconstruction error anomaly vectors into instant software-defined configuration changes (Kubernetes `NetworkPolicies` or Istio proxy blocks) in real-time.
- **Explainable Remediation Loop**: Integrating black-box anomaly detectors directly with local LLMs to output human-readable triage justifications and IaC configuration patches concurrently.
- **Performance Profiling of PQC in Containers**: Benchmarking the resource footprint (CPU, memory, connection latency) of running hybrid ECC-PQC authentication libraries inside container sidecars.

---

## 3. Feasible Gaps for a University Internship
- **Deploying a Local Anomaly-to-Policy Loop**: Setting up a lightweight Autoencoder container sidecar that triggers a local Kubernetes policy script when resource usage or network traffic exhibits reconstruction error anomalies. This is highly realistic using standard Python, Ansible, and Docker.
- **PQC Performance Benchmarking**: Integrating liboqs inside a Python backend service and executing load tests (ECC vs. Hybrid Kyber) to collect CPU and latency stats. This requires no custom cryptosystem engineering and is highly publishable.
- **LLM Triage Helper**: Using a lightweight local LLM (e.g. Llama-3B) with LangChain to consume anomaly alerts and suggest Terraform edits. This leverages existing APIs and RAG workflows.

---

## 4. Technology Combination for Strongest Contribution

By combining the following technologies, we create a highly novel, integrated security framework:

$$\text{Telemetry (eBPF/Prometheus)} + \text{AI (Autoencoder anomaly scores)} + \text{Zero Trust (OPA RiskPDP)} + \text{Automation (Kubernetes policies)} + \text{PQC (liboqs benchmarks)}$$

This combination ensures we solve:
1. **The Performance Bottleneck**: Utilizing lightweight local autoencoders.
2. **The Explainability Gap**: Incorporating LLM triage.
3. **The Migration Dilemma**: Providing concrete empirical data on PQC container overhead.
This delivers a strong contribution without requiring the implementation of new AI models or cryptographic algorithms, directly matching our university research objectives.
