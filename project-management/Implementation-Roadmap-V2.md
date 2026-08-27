# Project Implementation Roadmap (Version 2.0)

This roadmap details the objectives, deliverables, timelines, dependencies, and owners across the eight development milestones of the framework.

---

## Milestone 1: Backend Foundation
- **Objectives**: Initialize backend microservice frameworks, establish MongoDB database connection metrics, and draft service communication endpoints.
- **Deliverables**: Express API baseline code, docker-compose template for local MongoDB instances, API index routes.
- **Estimated Time**: 2 Weeks.
- **Dependencies**: None.
- **Owner**: Devam.

---

## Milestone 2: Authentication
- **Objectives**: Implement admin registration, signature challenge generation, and Elliptic Curve Cryptography (ECC) verification. Configure JWT validation.
- **Deliverables**: Challenge endpoint, public key repository schema, validation wrapper class, JWT issuance/revocation controller.
- **Estimated Time**: 2 Weeks.
- **Dependencies**: Milestone 1.
- **Owner**: Kalpesh.

---

## Milestone 3: Monitoring
- **Objectives**: Deploy Node Exporter and Prometheus scrapers across cluster namespaces. Expose system resource metrics endpoints to the backend.
- **Deliverables**: Prometheus config maps, scraping target manifests, backend routes translating metric formats.
- **Estimated Time**: 2 Weeks.
- **Dependencies**: Milestone 1.
- **Owner**: Devam.

---

## Milestone 4: AI Engine
- **Objectives**: Develop the local feature scaling, PCA dimensionality reduction class, and PyTorch unsupervised Autoencoder/Isolation Forest core.
- **Deliverables**: Training logs preprocessor class, Autoencoder neural network model, inference endpoint outputting reconstruction loss.
- **Estimated Time**: 3 Weeks.
- **Dependencies**: Milestone 3.
- **Owner**: Dil.

---

## Milestone 5: Risk Engine
- **Objectives**: Translate raw model reconstruction losses into Unified Risk Scores, applying host weights.
- **Deliverables**: Criticality metadata database records, risk score calculator route.
- **Estimated Time**: 1 Week.
- **Dependencies**: Milestone 4.
- **Owner**: Dil.

---

## Milestone 6: Automation
- **Objectives**: Configure OPA policy decision logic, build Ansible containment playbooks, and create Kubernetes dynamic NetworkPolicy isolation tasks.
- **Deliverables**: OPA policies, Ansible playbooks, execution shell controllers.
- **Estimated Time**: 2 Weeks.
- **Dependencies**: Milestone 5.
- **Owner**: Devam.

---

## Milestone 7: Dashboard
- **Objectives**: Create the frontend React layout displaying cluster states. Connect live socket alert notification streams.
- **Deliverables**: React dashboard UI panels, WebSocket server connection layer.
- **Estimated Time**: 2 Weeks.
- **Dependencies**: Milestone 6.
- **Owner**: Devam.

---

## Milestone 8: Experiments
- **Objectives**: Execute load tests, simulate attack flows, document connection latencies, and compile performance metrics (ECC vs. PQC handshakes).
- **Deliverables**: Performance datasets, telemetry charts, thesis data table outputs.
- **Estimated Time**: 2 Weeks.
- **Dependencies**: Milestone 7.
- **Owner**: Shivraj (PQC / Quantum) & Dil (AI).
