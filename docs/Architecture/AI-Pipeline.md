# Artificial Intelligence Pipeline Specification

This document details the telemetry ingestion, feature processing, modeling, risk assessment, and decision logic utilized in the framework.

---

## 1. Pipeline Overview

The pipeline is built around lightweight, unsupervised anomaly detection designed to minimize computational latency on Kubernetes cluster nodes.

```
+------------------+
|   Prometheus     | (Syslog, Network Counters, CPU/Memory telemetry)
+--------+---------+
         | JSON streams
         v
+--------+---------+
| Feature Engine   | (Min-Max Scaling, PCA Dimensionality Reduction)
+--------+---------+
         | Scaled Float Vector
         v
+--------+---------+
| AI Detector Core | (Unsupervised PyTorch Autoencoder / Isolation Forest)
+--------+---------+
         | Reconstruction Loss
         v
+--------+---------+
| Risk Scoring     | (Asset Criticality mapping -> Score 0-100)
+--------+---------+
         | Risk Score
         v
+--------+---------+
| Decision Engine  | (ZTA Threshold check -> triggers playbook)
+------------------+
```

---

## 2. Ingestion & Preprocessing

### 2.1. Data Sources
The pipeline scrapes real-time container metrics using Prometheus client daemons and Node Exporter:
- **Network Telemetry**: `node_network_receive_bytes_total`, `node_network_transmit_packets_total`, socket packet drop logs.
- **Resource Telemetry**: `container_cpu_usage_seconds_total`, `container_memory_working_set_bytes`.
- **System Event Logs**: Node kernel event traces.

### 2.2. Preprocessing & Feature Engineering
To prevent high-dimensional logs from slowing down predictions:
1. **Normalization**: Numerical inputs are scaled using Min-Max Normalization:
   $$x_{scaled} = \frac{x - x_{min}}{x_{max} - x_{min}}$$
2. **PCA Reduction**: Principal Component Analysis (PCA) maps the normalized vector into a lower-dimension space (retaining 95% of data variance), reducing input features from over 40 variables to 6 principal components. This cuts classification execution latency by 40% (evidence from P09).

---

## 3. Modeling Core (Lightweight AI)

The framework utilizes an unsupervised **Deep Autoencoder** (or **Isolation Forest** depending on deploy parameters). Unsupervised approaches are preferred because they do not require labeled attack signatures, allowing detection of zero-day attacks (evidence from P01, P04, P05).

### 3.1. Autoencoder Architecture
- **Input Layer**: $d$ dimensions (e.g., 6 after PCA).
- **Encoder**: Fully connected layers decreasing dimensions to a bottleneck latent space (dimension 2).
- **Decoder**: Fully connected layers expanding back to $d$ dimensions.
- **Activation**: ReLU on intermediate layers, Sigmoid on output.

### 3.2. Training (Offline / Asynchronous)
- **Objective**: Train only on verified "normal" system telemetry logs to learn baseline operations.
- **Loss Function**: Mean Squared Error (MSE) representing Reconstruction Loss:
   $$L(x, \hat{x}) = \frac{1}{d} \sum_{i=1}^{d} (x_i - \hat{x}_i)^2$$
- **Optimization**: Adam optimizer, batch size 64. Trained on a background worker thread to prevent pipeline deployment blockages.

### 3.3. Inference (Online)
- The Telemetry Collector forwards scaled runtime vectors through the trained encoder-decoder.
- Computes reconstruction loss $L$. If $L > \tau$ (where $\tau$ is a threshold calculated from the 99th percentile of baseline training loss), the flow is classified as anomalous.

---

## 4. Risk Score & Decision Logic

### 4.1. Risk Score Calculation
Raw reconstruction loss $L$ is normalized into a dynamic **Unified Risk Score (URS)** ranging from 0 to 100:
$$URS = \min\left(100, \left( \frac{L}{\tau} \times 50 \times \alpha \right)\right)$$
Where:
- $\tau$ is the anomaly threshold.
- $\alpha$ is the **Asset Criticality Weight** (e.g., 1.5 for auth API gateway, 1.0 for worker pods). If $URS \ge 50$, the event is flagged.

### 4.2. Decision Logic & Automation Trigger
The Decision Engine (Policy PDP) evaluates the URS using Zero-Trust policies:

```python
def evaluate_risk(urs, policy):
    if urs >= policy.risk_threshold:
        if policy.auto_mitigate:
            trigger_automation(policy.action_type)
            log_response(policy.name, policy.action_type)
        else:
            send_alert_to_dashboard(urs)
```

- **Trigger Actions**:
  - `Kubernetes NetworkPolicy` isolation: isolates the target pod.
  - `Ansible Playbook` restart: rebuilds/re-provisions the node.

---

## 5. Logging & Evaluation
- **Logging**: Execution paths are written directly to MongoDB `ThreatEvents` and `Responses` collections.
- **Evaluation Metrics**:
  - **FPR (False Positive Rate)**: Targeted at <1% to prevent security operator alert fatigue.
  - **Overhead**: Telemetry extraction overhead must remain <5% CPU to satisfy performance metrics (P07).
