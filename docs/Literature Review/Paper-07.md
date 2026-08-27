# Paper 07: Advancing Software Security and Reliability in Cloud Platforms through AI-based Anomaly Detection

## Bibliographic Information
- **Title**: Advancing Software Security and Reliability in Cloud Platforms through AI-based Anomaly Detection
- **Authors**: Sabbir M. Saleh, Ibrahim Mohammed Sayem, Nazim Madhavji, John Steinbacher
- **Year**: 2024
- **Journal/Conference**: Proceedings of the 2024 ACM Cloud Computing Security Workshop (CCSW '24) / arXiv preprint arXiv:2411.09200
- **Publisher**: ACM
- **DOI**: 10.1145/3689938.3694779
- **URL**: [https://arxiv.org/abs/2411.09200](https://arxiv.org/abs/2411.09200)

## Executive Summary
This paper addresses the security of Continuous Integration/Continuous Deployment (CI/CD) pipelines in cloud platforms by implementing an AI-based network anomaly detection system using a hybrid CNN-LSTM architecture. The goal is to detect cyberattacks (such as DDoS and Botnets) targeting pipeline runners and cloud infrastructure.

## Technical Summary
The authors present a pipeline-level traffic monitoring framework. By co-locating traffic monitoring agents near CI/CD runners, network patterns are parsed and fed to a hybrid Convolutional Neural Network (CNN) and Long Short-Term Memory (LSTM) network. CNN is utilized to extract spatial features of packet streams, and LSTM is utilized to trace temporal dependency changes.

## Architecture
- **Monitoring Agents**: Local network logging agents capturing packet headers and traffic metrics from cloud servers.
- **Preprocessing Engine**: Parses raw traffic into standard tabular flow metrics.
- **Hybrid Classifier Model**: CNN-LSTM network classifying flows as normal or attack.
- **Reporting Pipeline**: Automatically writes log records mapping detected anomalies to corresponding pipeline stages (Code build, test, deploy).

## Algorithms
- **Convolutional Neural Network (CNN)** (for spatial feature extraction).
- **Long Short-Term Memory (LSTM)** (for temporal classification).
- **Hybrid CNN-LSTM**.

## Technologies
- **Jenkins**, **Docker**, **Prometheus**, **Python (TensorFlow/Keras)**, **Git**.

## Dataset
- **CSE-CIC-IDS2018** and **CSE-CIC-IDS2017** network traffic benchmarks.

## Experimental Results
- Evaluated on CSE-CIC-IDS2018 and CSE-CIC-IDS2017 datasets:
  - **Accuracy**: **98.69%** (CSE-CIC-IDS2018) and **98.30%** (CSE-CIC-IDS2017).
  - Successfully generated trace log alerts inside CI/CD runners matching simulated intrusion timestamps.

## Strengths
- Focuses on securing the CI/CD pipeline infrastructure itself rather than just the code artifacts.
- Incorporates a mathematically rigorous CNN-LSTM model with high validation metrics.

## Author Reported Limitations
- Heavy computational overhead of the combined CNN-LSTM model, making real-time, low-latency execution difficult under high network throughput.
- Dependence on static, offline training datasets that do not adapt dynamically to new zero-day attacks.

## Future Work
- Designing adaptive, low-latency traffic mitigation mechanisms (e.g., automated firewall blocks).
- Evaluating performance overhead across different cloud architectures.

## Important Concepts
- **Spatial-Temporal Intrusion Profiling**: Analyzing both the shape and sequence of packet streams to detect multi-stage attacks.
- **Runner-Level Telemetry**: Logging network state directly inside CI/CD execution contexts.

## Our Observations
- Confirms the feasibility of deploying deep learning models to secure cloud pipeline infrastructure. Validates the performance trade-off between detection accuracy and latency overhead.

## Relevance to Our Research
- High. Direct evidence of using hybrid deep learning to monitor cloud-native CI/CD infrastructure, highlighting the need for low-overhead models in active environments.

## Possible Adoption
- Incorporating network telemetry monitoring for our Kubernetes pipelines, but evaluating autoencoders or simpler classifiers to reduce runner CPU overhead.
