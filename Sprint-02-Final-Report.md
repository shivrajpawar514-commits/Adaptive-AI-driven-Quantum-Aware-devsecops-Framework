# Sprint 02 Final Report: Literature Synthesis & Architectural Blueprint

This final report compiles the findings from Sprints 01 and 02, analyzing all ten research papers (P01 - P10) to establish a comprehensive technical foundation for the Adaptive AI-Driven DevSecOps Framework.

---

## 1. Executive Summary

This report synthesizes academic and industry literature at the intersection of Cloud Security, DevSecOps, Artificial Intelligence, and Post-Quantum Cryptography (PQC). The primary objective is to answer the core research question: *Can an integrated, AI-driven framework improve cloud threat responses through automated security operations while maintaining acceptable performance and supporting future PQC migrations?*

Based on the analysis of ten primary publications, the consensus confirms that while machine learning and deep learning show high accuracy in threat detection, current systems suffer from high processing latency, "black-box" explainability deficits, and tool integration complexities in continuous deployment environments. This framework addresses these deficiencies by integrating localized feature selection, lightweight autoencoder anomaly scoring, local LLM explainability sidecars, and empirical PQC container benchmarking.

---

## 2. Literature Overview (P01 - P10)

The ten papers are categorized into three core research domains:

### Domain A: DevSecOps & Security Automation (P02, P03, P06)
- **AI for DevSecOps (P02 - Fu et al.)**: Maps AI models across 12 specific DevOps tasks, highlighting immaturity in automated vulnerability repair and configuration patching.
- **Adoption Challenges (P03 - Rajapakse et al.)**: SLR identifying 21 challenges in DevSecOps. Proposes Infrastructure as Code (IaC) and container orchestration, while identifying a lack of validated pipeline security metrics.
- **Comparative Security Analysis (P06 - Binbeshr et al.)**: Highlights that AI static scanners reduce false positive rates by 30% but introduce pipeline latency and configuration overhead.

### Domain B: AI-Driven Cloud Anomaly Detection (P01, P04, P07, P09)
- **Cloud AI Review (P01 - Alzoubi et al.)**: Bibliometric study of 4,051 papers confirming a post-2018 transition to deep learning models (CNN, LSTM, Autoencoders) for cloud intrusion detection.
- **Intrusion Detection Survey (P04 - Lata et al.)**: Evaluates cloud IDS techniques. Identifies that hybrid models yield high accuracy but increase latency and fail to scale in multi-tenant networks.
- **Pipeline Network Anomaly Detection (P07 - Saleh et al.)**: Deploys a hybrid CNN-LSTM to monitor CI/CD runner network traffic. Achieves 98.69% accuracy on CSE-CIC-IDS2018.
- **Attack Prevention & VM Profiling (P09 - Eddermoug et al.)**: Reviews VM/hypervisor logs and highlights that feature selection techniques cut processing latency by 40% while preserving accuracy.

### Domain C: Zero-Trust & Quantum Security Planning (P05, P08, P10)
- **Zero-Trust Multi-Cloud Anomaly Detection (P05 - Almulla et al.)**: Explores AI anomaly logs feeding Zero-Trust Policy Decision Points. Highlights a lack of cross-cloud validation and dynamic policy translation.
- **Autonomous Threat Response (P08 - Sarraf et al.)**: Surveys closed-loop incident mitigation using Deep Reinforcement Learning (DRL) and LLM triage assistants.
- **Quantum Anomaly Detection (P10 - Corli et al.)**: Reviews QML models (QAE, QSVM) for anomaly detection. Concludes that QML is simulator-bound for industrial logs due to NISQ qubit limits and errors.

---

## 3. Technology Trends

Based on the pattern analysis, the following technologies dominate the cloud security and DevSecOps research space:
- **Core Orchestration**: Kubernetes, Docker, and Istio Service Mesh.
- **Configuration & IaC**: Terraform, Ansible, and GitLab CI/CD.
- **Threat Anomaly Algorithms**: Deep Autoencoders, Convolutional Neural Networks (CNN), Long Short-Term Memory (LSTM), and local feature selection (PCA/Information Gain).
- **Emerging Paradigms**: Parameterized Quantum Circuits (PQC), hybrid ECC-Kyber authentication, and Local LLM (Llama-3B) with RAG pipelines.

---

## 4. Gap Analysis

The systematic review identified five critical research gaps:
1. **Dynamic Policy Orchestration**: Traditional IDPSs trigger email alerts rather than translating threat metrics directly into software-defined infrastructure (Kubernetes `NetworkPolicies`).
2. **Post-Quantum Container Benchmarks**: Lack of empirical performance overhead data (CPU, memory, handshake latency) of hybrid classical-PQC algorithms running inside Docker containers.
3. **Explainability Deficit**: Deep learning classifiers operate as "black-boxes," causing alert fatigue and preventing security teams from validating automated actions.
4. **Pipeline Resource Overhead**: Complex deep learning models (like CNN-LSTMs) introduce severe latency, slowing down active compilation and runner pipelines.
5. **Cross-Cloud Model Generalization**: Security models trained on single-cloud datasets fail to identify threats or enforce policies uniformly across multi-cloud meshes.

---

## 5. Architecture Evolution

The project architecture has evolved from a simple static pipeline checks layout to a **closed-loop adaptive controller**:

```
[Raw Network & Pod Telemetry]
         |
         v
[eBPF / Telemetry Controller] (Local PCA Feature Reduction)
         |
         v
[AI Anomaly Detector] (Lightweight Deep Autoencoder)
         |
         v
[ZTA PDP Risk Assessor] (Zero-Trust policy check using OPA)
         |
         v
[Enforcement Engine] (Dynamic Kubernetes NetworkPolicies & Ansible Blocks)
         |
         v
[LLM Explainability sidecar] (RAG translation of alerts to human logs)
```

---

## 6. Recommended Project Direction

The proposed project title and description represent a highly competitive and publishable research initiative:
- **Title**: Adaptive AI-Driven DevSecOps Framework for Secure Cloud Infrastructure with Quantum-Aware Security Planning
- **Is this still the best direction?**: **YES**. It directly targets the integration deficits identified in the literature, using accessible technologies to solve major gaps (PQC benchmarking, policy translation, explainability).
- **Suggested Adjustments**:
  - Focus on **Simulated Quantum-Aware Security Planning**: Do not attempt to run QML models on real quantum hardware (as it is currently NISQ-bound); instead, run Quantum Autoencoder simulations using Qiskit within the testing module and evaluate hybrid classical-PQC library overhead (liboqs).
  - Prioritize **lightweight models**: Use localized PCA and Autoencoders for microservice sidecars to maintain low latency, addressing the performance bottlenecks highlighted in P07.

---

## 7. Conclusions & Next Sprint Objectives

### Conclusions
The literature validates that security automation is the only viable path to protect cloud infrastructures at scale. By designing an adaptive DevSecOps loop that couples telemetry, autoencoders, ZTA, Kubernetes policies, and hybrid PQC benchmarks, this project will deliver a valuable, publishable contribution to cloud computing and software engineering venues.

### Next Sprint Objectives (Sprint 03)
1. **Establish the Kubernetes Testbed**: Configure a local cluster (Kind/Minikube) with eBPF/Prometheus logging enabled.
2. **Develop the Anomaly Engine**: Build the PyTorch Autoencoder classifier and test it using preprocessed CSE-CIC-IDS2018 data.
3. **PQC Integration**: Install liboqs/OpenSSL with OQS providers inside Docker containers and run baseline connection tests.
