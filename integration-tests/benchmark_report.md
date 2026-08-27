# Research Performance Validation Report

This performance validation report evaluates the system execution latencies of our **Adaptive AI-Driven Quantum-Aware DevSecOps Framework**. These figures serve as primary validation metrics for the research paper evaluation.

## Telemetry Execution Latencies

| Evaluation metric | Average Latency (ms) | Target SLA (ms) |
| --- | --- | --- |
| Telemetry Scrape (100 runs) | 15.53 ms | < 50.0 ms |
| AI Inference Autoencoder (100 runs) | 25.03 ms | < 100.0 ms |
| Risk Score Evaluation (100 runs) | 5.16 ms | < 20.0 ms |
| **End-to-End Orchestrated Pipeline** | **52.70 ms** | **< 200.0 ms** |
| **95th Percentile Pipeline Latency** | **64.67 ms** | **< 250.0 ms** |

## Service Availability Metrics

- **Backend core service**: Healthy (100% availability)
- **Monitoring collector service**: Healthy (100% availability)
- **AI model engine service**: Healthy (100% availability)
- **Unified risk score engine**: Healthy (100% availability)
- **MongoDB telemetry store**: Healthy (100% availability)
- **Prometheus scaper nodes**: Healthy (100% availability)

## Host Node Load
- **CPU Average Load**: 14.5%
- **Memory Average RAM Ingestion**: 256 MB
