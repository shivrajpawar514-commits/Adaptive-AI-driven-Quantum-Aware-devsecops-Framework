# Sprint 02: Pattern Analysis

This document synthesizes key patterns, technologies, algorithms, and methodologies identified across all ten analyzed research papers (P01 - P10).

---

## 1. Technological & Tooling Patterns

### Most Common Cloud Technologies
- **Containerization & Orchestration**: **Docker** and **Kubernetes** are the standard platforms for modern cloud-native deployments (P02, P03, P05, P06, P07, P08).
- **Virtualization & Hypervisors**: Legacy virtual machines running on hypervisors (Xen, KVM) are evaluated in older intrusion surveys, but container-based virtualization is dominant in newer works (P04, P09).
- **Cloud Infrastructure Logging**: Virtual Private Cloud (VPC) network logs, system event logs, host CPU/memory telemetry, and cloud trail audit trails (P01, P05, P07, P08, P09).

### Most Common DevSecOps Tools
- **Automation & Orchestration**: **Jenkins**, **GitLab CI**, and **GitHub Actions** are the primary continuous integration and continuous deployment (CI/CD) orchestrators (P02, P03, P06, P07).
- **Infrastructure as Code (IaC)**: **Terraform** and **Ansible** are widely discussed for provisioning and configuration management (P02, P03, P06, P08).
- **Security Checkpoints**: Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), and **Interactive Application Security Testing (IAST)** (P02, P03, P06).

### Most Common Security Techniques
- **Intrusion Detection/Prevention (IDS/IPS)**: Classifying host-level (HIDS) and network-level (NIDS) security profiles (P04, P07, P09).
- **Zero-Trust Architecture (ZTA)**: Runtime policy enforcement points, identity providers (IdP), micro-segmentation, and dynamic context-aware risk evaluations (P01, P04, P05, P08, P10).
- **Security Automation (SOAR)**: Closed-loop mitigation tools like dynamic container isolation or session revocation (P05, P08).

---

## 2. Artificial Intelligence & Algorithmic Patterns

### Most Common AI Algorithms
- **Classical Machine Learning**: Support Vector Machines (**SVM**), **Random Forest** (RF), **K-Nearest Neighbors** (k-NN), Decision Trees, and K-means clustering (P01, P02, P04, P05, P06, P08, P09).
- **Deep Learning**: **Convolutional Neural Networks** (CNN), **Long Short-Term Memory** (LSTM) networks, spatial-temporal hybrids (**Conv-LSTM**), and **Autoencoders** (P01, P02, P04, P05, P06, P07, P08, P09).
- **Generative AI & LLMs**: Transformer-based models for software vulnerability classification and query extraction (P02, P08).
- **Reinforcement Learning**: Deep Reinforcement Learning (**DRL**) with Q-networks for automated pathfinding and incident mitigation (P08, P10).
- **Quantum Machine Learning**: **Quantum Autoencoders** (QAE), Parameterized Quantum Circuits (PQC), and Quantum Support Vector Machines (QSVM) (P10).

---

## 3. Evaluation & Experimental Data Patterns

### Most Common Datasets
- **KDD99 / NSL-KDD**: Still widely used in academic settings despite heavy criticism for lack of modern network protocols and redundancy (P01, P04, P05, P09, P10).
- **UNSW-NB15**: Frequently selected to capture contemporary attack signatures and realistic protocol variety (P04, P05, P09).
- **CSE-CIC-IDS2017 / CSE-CIC-IDS2018**: The gold standard for modern network intrusion evaluation due to realistic background traffic and updated threat scenarios (P04, P05, P07).
- **Juliet Test Suite**: Used for code-centric vulnerability evaluation (P06).

### Most Common Evaluation Metrics
- **Classification Performance**: **Accuracy**, **Precision**, **Recall**, **F1-Score**, and **ROC AUC** (P01, P02, P04, P05, P06, P07, P08, P09, P10).
- **Operational Efficiency**: **False Positive Rate (FPR)** (critical for measuring alert fatigue), **Detection Rate (DR)**, and processing throughput (P04, P05, P09).
- **Computational Overhead**: Pipeline compilation latency, CPU and memory footprint, training/inference time, and quantum gate depth (P01, P02, P04, P07, P09, P10).

---

## 4. Synthesis of Gaps, Trends, & Limitations

### Frequently Repeated Limitations
1. **Computational Latency**: Deep learning models introduce severe computational delays that disrupt real-time network and pipeline environments (P01, P02, P04, P07, P09).
2. **Explainability Deficit**: Complex models act as "black-boxes," causing alert fatigue and preventing security teams from validating automated actions (P01, P02, P04, P08, P09, P10).
3. **Data Quality & Bias**: Heavy reliance on clean labeled datasets and outdated benchmarks (KDD99) that do not reflect containerized microservices (P01, P04, P05, P09, P10).
4. **Remediation Ineffectiveness**: High failure rates when AI attempts to dynamically generate code patches or rewrite configuration files (P02, P08).
5. **NISQ Hardware Bottlenecks**: Quantum machine learning remains limited by qubit counts, coherence errors, and state-preparation overhead (P10).

### Research Trends
- **Transition from ML to Deep Learning**: CNNs and Autoencoders are preferred over simple classifiers to capture high-dimensional interactions (P01, P04).
- **Continuous Compliance & Shift-Left Policy**: Integrating OPA and dynamic policy scanners early in CI/CD (P02, P03).
- **Active Remediation (SOAR)**: Shifting from passive anomaly alerts to self-healing software-defined infrastructures (P05, P08).
- **Large Language Models (LLMs)**: Ingesting code context and security events to explain anomalies and assist engineers (P02, P08).

### Technologies Becoming Popular
- **Post-Quantum Cryptography (PQC)** (in transition phase from classical protocols).
- **Explainable AI (XAI)** (SHAP, LIME).
- **Zero-Trust (ZTA)** integration with runtime telemetry.

### Technologies Rarely Explored
- **Hybrid PQC-ECC performance profiling in containers**: Evaluating actual gate latency of hybrid keys inside Kubernetes sidecars.
- **Dynamic AI-to-Policy translation**: Autonomous translation of anomaly scores into Kubernetes NetworkPolicies or Istio rules.

---

## 5. Summary of Implementation & Automation Deficits

| Dimension | Deficit / Gaps Identified in Literature |
| :--- | :--- |
| **Lacking Implementation** | - Standardized middleware mapping AI anomaly scores directly to container security group configurations (P05, P08).<br>- Empirical deployments of post-quantum cryptographic libraries within orchestrated container mesh networks (P03). |
| **Lacking Experimentation** | - Real-world, cross-cloud validation of trained anomaly models (most models are validated on single testbeds) (P01, P05).<br>- Performance overhead profiles of hybrid classical-PQC authentication under heavy network load (P03). |
| **Lacking Automation** | - High-accuracy, autonomous vulnerability patch remediation (P02, P08).<br>- Synchronized policy propagation across multi-cloud providers based on dynamic local threat profiles (P05). |
