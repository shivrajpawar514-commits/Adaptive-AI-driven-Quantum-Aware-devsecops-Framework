# Future Sprint Execution Plan (Sprints 05 - 10)

This plan outlines the objectives, focus areas, and milestone mappings for the remaining sprints of the internship project.

---

## Sprint 05: AI Pipeline Optimization & Preprocessing
- **Focus**: Integrating feature scaling pipelines and model validations.
- **Objectives**:
  - Run continuous baseline telemetry tests to train the Autoencoder model on "normal" workloads.
  - Optimize the local PCA reducer to minimize package feature selection time (target <1ms per feature frame).
  - Verify that the Reconstruction Loss threshold $\tau$ scales dynamically with varying CPU workloads without false positive alarms.

---

## Sprint 06: Zero-Trust Decision Engine & SOAR Automation
- **Focus**: Hardening PEP enforcement latency and OPA rules.
- **Objectives**:
  - Integrate Open Policy Agent (OPA) with the Decision Engine (RiskPDP) to validate URS scores against YAML policies.
  - Implement full mutual TLS (mTLS) for all backend-to-Kubernetes API triggers.
  - Test response MTTR latency (target <150ms for container isolation, <2 seconds for node firewall updates).

---

## Sprint 07: Web Security Dashboard & Websocket Portal
- **Focus**: Visual telemetry UI integration and user notifications.
- **Objectives**:
  - Connect the React frontend application to the Express WebSocket server.
  - Implement live dynamic log tables displaying anomalous threat parameters.
  - Design interactive client UI panels enabling administrators to adjust active policy risk thresholds.

---

## Sprint 08: Quantum Simulation & PQC Benchmarking
- **Focus**: Bloch Sphere models and post-quantum container tests.
- **Objectives**:
  - Develop Python Qiskit models simulating Bloch Sphere qubit rotations for anomaly classifications.
  - Deploy standard PQC libraries (ML-KEM/ML-DSA via liboqs) inside Docker containers.
  - Benchmark connections under Locust load test suites (ECC vs. Hybrid PQC throughput and CPU metrics).

---

## Sprint 09: System Integration & Security Dry Runs
- **Focus**: Load tests and simulated attack vectors validation.
- **Objectives**:
  - Execute multi-stage attack scripts (DDoS, Botnets, API privilege escalation) in local testbeds.
  - Profile the combined resource utilization (CPU, memory, packet drops) of all container sidecars.
  - Compile the experimental data results logs in MongoDB.

---

## Sprint 10: Academic Paper Compilation & Thesis Submission
- **Focus**: Manuscript drafting and submission.
- **Objectives**:
  - Export experiment results to tabular matrices and generate EPS plots for LaTeX formatting.
  - Draft the research manuscript in double-column IEEE template format.
  - Review technical citations and bibliography mapping.
  - Complete paper reviews and submit the manuscript to targeted venues.
