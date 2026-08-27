# Software Architecture Design (Version 1.0)

This document describes the high-level architecture, subsystems, interactions, and data flows of the Adaptive AI-Driven DevSecOps Framework for Secure Cloud Infrastructure.

---

## 1. High-Level Architecture

The framework is designed as a modular, containerized platform deployed within a Kubernetes cluster. It bridges continuous pipeline security (DevSecOps) with real-time runtime monitoring, Zero-Trust policy enforcement, and simulated quantum-safe migration.

```
       +-----------------------------------------------------------------+
       |                       CI/CD WORKFLOW RUNNERS                    |
       |  [Git / Jenkins] -> [Terraform/Ansible] -> [Docker Build/Push]  |
       +--------------------------------+--------------------------------+
                                        | Deploys to
                                        v
+---------------------------------------+---------------------------------------+
|                               KUBERNETES CLUSTER                              |
|                                                                               |
|   +--------------------------+                 +--------------------------+   |
|   |  MICROSERVICES RUNTIME   |                 |   TELEMETRY CONTROLLER   |   |
|   |  - API Pods (Hybrid PQC) |    Telemetry    |  - eBPF / Prometheus     |   |
|   |  - Monitoring Sidecars   |---------------->|  - local PCA Reducer     |   |
|   |  - Istio Mesh Proxies    |                 +------------+-------------+   |
|   +--------------------------+                              |                 |
|                ^                                            v                 |
|                | Reconfigures                               | Real-time Logs  |
|                |                                            v                 |
|   +------------+-------------+                 +------------+-------------+   |
|   |    ENFORCEMENT ENGINE    |                 |    AI ANOMALY DETECTOR   |   |
|   |  - OPA Gatekeeper        |   Mitigation    |  - Deep Autoencoder      |   |
|   |  - Ansible Playbooks     |<----------------|  - Risk Assessor (PDP)   |   |
|   |  - Dynamic NetPolicies   |      Paths      +------------+-------------+   |
|   +--------------------------+                              |                 |
|                                                             | Anomaly Vector  |
|                                                             v                 |
|                                                +------------+-------------+   |
|                                                | LLM REMEDIATION AID (RAG)|   |
|                                                |  - Triage Assistant      |   |
|                                                |  - Explainer Interface   |   |
|                                                +--------------------------+   |
+-------------------------------------------------------------------------------+
```

---

## 2. Subsystems & Responsibilities

### 2.1. Telemetry Controller
- **Responsibilities**: Gathers active runtime telemetry (network socket state, packet rates, memory usage, API call logs) from the Kubernetes pod namespaces.
- **Components**: Prometheus daemonset, eBPF logs.
- **Performance Optimization**: Executes localized feature selection (PCA/dimensionality reduction) to convert raw high-dimensional network captures into a compact tabular feature vector before transmission, cutting processing latency by up to 40% (evidence from P09).

### 2.2. AI Anomaly Detector & Risk Assessor (PDP)
- **Responsibilities**: Performs unsupervised anomaly detection on resource and network telemetry. Computes real-time context-aware risk scores for each workload.
- **Components**: Unsupervised Deep Autoencoder model trained on normal baseline logs. A threshold engine calculates reconstruction error anomalies.
- **Zero-Trust PDP**: Map-scores raw anomalies to specific Zero-Trust risk levels based on context (e.g. source IP, target port, credential state).

### 2.3. Enforcement Engine (PEP)
- **Responsibilities**: Executes automated threat containment and self-healing infrastructure adjustments.
- **Components**: Kubernetes custom controller, Open Policy Agent (OPA) gatekeeper, and Ansible playbooks.
- **Mitigation Actions**: Dynamically patches Kubernetes `NetworkPolicies` or changes Istio authorization filters to isolate anomalous pods, blocking traffic in <100ms (evidence from P08).

### 2.4. LLM Remediation & Explainability Aid
- **Responsibilities**: Resolves the "black-box" explainability gap of the AI detector. Automatically translates alerts into human-readable incident summaries and generates IaC patches.
- **Components**: Local Llama/Mistral inference engine, LangChain pipeline, and vector DB populated with CVE and configuration rules (RAG).

### 2.5. Post-Quantum Cryptography (PQC) benchmark harness
- **Responsibilities**: Profiles the system performance impact of quantum-safe cryptographic algorithms.
- **Components**: Microservice testbeds running hybrid ECC-ML-KEM (Kyber) and ECC-ML-DSA (Dilithium) authentication via liboqs, paired with locust load testers to document CPU/memory/latency curves.

---

## 3. Module Interactions & Data Flow

### Sequence of Events (Detection and Self-Healing Loop)
1. **Input**: Real-time network packets and microservice events hit the **Telemetry Controller**.
2. **Preprocessing**: The Controller performs feature selection and forwards a reduced vector to the **AI Anomaly Detector**.
3. **Detection**: The Autoencoder computes the reconstruction error. If the error exceeds the threshold, an anomaly vector is flagged.
4. **Assessment**: The Risk Assessor evaluates the anomaly score along with context, generating a mitigation path.
5. **Mitigation**: The **Enforcement Engine** executes a Kubernetes label update or triggers an Ansible playbook, isolating the target pod.
6. **Explanation**: The **LLM Remediation Aid** ingests the anomaly details, outputs an explanation card (*"Isolated pod due to SQL injection sequence on port 8080"*), and suggests a patch to the Terraform configuration.
7. **Output**: The explanation card and active container state are updated on the Security Dashboard.

---

## 4. Technology Stack
- **Cloud Infrastructure**: AWS VPC, Kubernetes (Kind/Minikube).
- **Automation & IaC**: Terraform, Ansible, Git.
- **Telemetry & Monitoring**: Prometheus, OpenTelemetry, eBPF logs.
- **AI & Explainability**: Python (PyTorch, Scikit-Learn), LangChain, Local LLM.
- **Quantum-Aware Cryptography**: OpenSSL with OQS provider (liboqs).
- **Policy Enforcement**: Open Policy Agent (OPA), Kubernetes NetworkPolicies.

---

## 5. Future Expansion Points
- **Quantum Simulator Integration**: Upgrading simulator tests from local Qiskit representations to physical quantum processors as qubit capacities scale.
- **Multi-Cloud Policy Syncer**: A gateway module to translate local container isolation decisions into AWS Security Group changes or GCP Firewall configurations dynamically.
