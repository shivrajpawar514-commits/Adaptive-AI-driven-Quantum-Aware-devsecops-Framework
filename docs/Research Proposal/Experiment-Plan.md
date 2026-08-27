# System Experimentation Plan

This document details the eight experiments designed to evaluate the accuracy, performance, resource footprint, and latency of the framework.

---

## 1. Experiment 1: Threat Detection Accuracy
- **Objective**: Measure the classification accuracy of the lightweight AI model (Autoencoder / Isolation Forest) under different attack injections.
- **Dataset**: CSE-CIC-IDS2018 network flows (representing DDoS, Botnets, and standard traffic).
- **Environment**: Isolated Kubernetes node executing the Python inference module.
- **Metrics**: Accuracy (%), Precision (%), Recall (%), F1-Score (%), ROC AUC.
- **Expected Graphs**: Confusion Matrix; ROC Curve comparing Autoencoder vs. Isolation Forest.
- **Expected Results**: Accuracy >96% for known DDoS patterns, with Isolation Forest converging faster but Autoencoder yielding higher recall.
- **Threats to Validity**: Domain mismatch if CSE-CIC-IDS2018 traffic characteristics differ significantly from live runtime telemetry.

---

## 2. Experiment 2: Automation Response Time (MTTR)
- **Objective**: Measure the time elapsed between anomaly classification and the initiation of automated containment (PEP execution).
- **Dataset**: Logged container event streams and simulated network threat alerts.
- **Environment**: Kubernetes cluster with the Decision Engine and Automation Engine.
- **Metrics**: Time-to-Respond (ms) (from risk generation to API command call).
- **Expected Graphs**: Box plot showing response latency variation over 100 runs.
- **Expected Results**: Response initiated in <50ms for local Kubernetes shell actions, and <250ms for Ansible playbook launches.
- **Threats to Validity**: Network API bottlenecks on the Kubernetes master node under heavy workloads.

---

## 3. Experiment 3: CPU Utilization
- **Objective**: Profile the CPU footprint of the Telemetry Collector, PCA reducer, and AI model during active monitoring.
- **Dataset**: Live microservice resource metrics collected over 24 hours.
- **Environment**: Prometheus monitoring agents scraping a Kubernetes node under continuous HTTP load.
- **Metrics**: CPU usage percentage (%).
- **Expected Graphs**: Line chart showing CPU usage over time with and without active AI sidecars.
- **Expected Results**: Combined CPU usage of security agents remains <5% of the total node allocation.
- **Threats to Validity**: Interference from background system processes running on the host OS.

---

## 4. Experiment 4: Memory Utilization
- **Objective**: Benchmark the memory footprint of the containerized security sidecars and Python processes.
- **Dataset**: Continuous container metrics logs.
- **Environment**: Kind/Minikube cluster nodes running the framework services.
- **Metrics**: Resident Set Size (RSS) memory consumption (MB).
- **Expected Graphs**: Bar chart comparing memory footprint: Telemetry Collector vs. AI Module vs. Quantum Bloch Simulator.
- **Expected Results**: Sidecar processes consume <128MB RAM, making them suitable for resource-constrained hosts.
- **Threats to Validity**: Python garbage collection delays causing temporary memory usage peaks.

---

## 5. Experiment 5: Container Recovery Time
- **Objective**: Measure the duration required to re-provision or restore an isolated pod namespace.
- **Dataset**: Automated restart and scale logs.
- **Environment**: Kubernetes cluster with automated restart scripts triggered by the Automation Engine.
- **Metrics**: Recovery time (seconds) (from isolation completion to pod status `Running`).
- **Expected Graphs**: Time-series curve showing traffic throughput recovery.
- **Expected Results**: Pod restoration completed in <8 seconds, achieving minimal system downtime.
- **Threats to Validity**: Docker registry download latency if container images are not cached locally.

---

## 6. Experiment 6: False Positive Rate (FPR)
- **Objective**: Verify that normal, benign client requests do not trigger false anomaly alerts.
- **Dataset**: CSE-CIC-IDS2017 clean traffic subset; live benign user traffic.
- **Environment**: Active microservice cluster subjected to simulated normal usage load.
- **Metrics**: False Positive Rate (%) (false alarms / total benign samples).
- **Expected Graphs**: Curve showing FPR variation across different reconstruction loss thresholds $\tau$.
- **Expected Results**: FPR remains <1.0% under typical usage workloads.
- **Threats to Validity**: Changes in user behavior patterns that simulate traffic bursts, skewing the model profile.

---

## 7. Experiment 7: Policy Enforcement Time
- **Objective**: Measure the execution latency of OPA gatekeepers and Ansible firewall adjustments.
- **Dataset**: Automated policy updates.
- **Environment**: Decision Engine evaluating REST payloads and writing policies.
- **Metrics**: Enforcement latency (ms) (from decision command to firewall/policy confirmation).
- **Expected Graphs**: Histogram mapping enforcement latencies across 100 runs.
- **Expected Results**: OPA policy evaluations complete in <5ms; Ansible node firewall changes execute in <2 seconds.
- **Threats to Validity**: Ansible SSH handshake delay on remote servers.

---

## 8. Experiment 8: Dashboard Alert Delay
- **Objective**: Measure the transmission latency of threat alerts from detection to dashboard visualization.
- **Dataset**: ThreatEvent logging records.
- **Environment**: Dashboard React UI connected via WebSockets to the Express backend.
- **Metrics**: Transmission delay (ms) (Dashboard receive timestamp minus ThreatEvent creation timestamp).
- **Expected Graphs**: Area chart showing latency variation over time under load.
- **Expected Results**: Alerts render in <300ms, providing real-time operator visibility.
- **Threats to Validity**: Browser rendering bottlenecks under high-volume alert bursts.
