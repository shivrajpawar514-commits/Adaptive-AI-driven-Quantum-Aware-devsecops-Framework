# Database Design Specification (MongoDB Collections)

This document details the MongoDB collections, fields, relationships, and indexes designed to support the logging, decision-making, and experimental analysis of the framework.

---

## 1. Collections Design

### 1.1. Collection: Users
- **Purpose**: Stores authentication credentials, cryptographic keys, and roles of system administrators.
- **Fields**:
  - `_id`: ObjectId (Primary Key)
  - `username`: String (Unique)
  - `email`: String (Unique)
  - `password_hash`: String (Argon2 or bcrypt hash)
  - `ecc_public_key`: String (PEM encoded ECC public key for signature validation)
  - `role`: String (e.g., `admin`, `auditor`, `developer`)
  - `created_at`: Date
  - `last_login`: Date
- **Relationships**:
  - One-to-Many with `SecurityLogs` (Admin activity history).
- **Indexes**:
  - `username` (Ascending, Unique)
  - `email` (Ascending, Unique)

### 1.2. Collection: ThreatEvents
- **Purpose**: Records anomaly detection alerts, computed risk scores, and attack vectors.
- **Fields**:
  - `_id`: ObjectId (Primary Key)
  - `timestamp`: Date
  - `source_ip`: String
  - `target_pod_id`: String (Kubernetes Pod UID reference)
  - `reconstruction_loss`: Double (Raw reconstruction score from Autoencoder)
  - `risk_score`: Integer (Unified score, 0-100)
  - `classification`: String (e.g., `Anomaly`, `Attack`, `Normal`)
  - `attack_type`: String (e.g., `DDoS`, `Botnet`, `Privilege Escalation`)
  - `remediation_triggered`: Boolean
- **Relationships**:
  - One-to-One with `Responses` (Mitigation logs).
- **Indexes**:
  - `timestamp` (Descending)
  - `target_pod_id` (Ascending)
  - `risk_score` (Descending)

### 1.3. Collection: SecurityLogs
- **Purpose**: Tracks operational, container, and pipeline actions for Zero-Trust verification.
- **Fields**:
  - `_id`: ObjectId (Primary Key)
  - `timestamp`: Date
  - `user_id`: ObjectId (Reference to `Users`, optional for system actions)
  - `action`: String (e.g., `Deploy Workload`, `Policy Update`, `Authentication Attempt`)
  - `status`: String (e.g., `Success`, `Failed`)
  - `details`: Object (Custom action metadata)
  - `client_ip`: String
- **Relationships**:
  - Many-to-One with `Users`.
- **Indexes**:
  - `timestamp` (Descending)
  - `user_id` (Ascending)

### 1.4. Collection: Policies
- **Purpose**: Stores Zero-Trust threat threshold rules and baseline profiles.
- **Fields**:
  - `_id`: ObjectId (Primary Key)
  - `name`: String (Unique, e.g., `Strict Pod Isolation`)
  - `risk_threshold`: Integer (0-100 threshold)
  - `auto_mitigate`: Boolean (Flag indicating if the engine should execute response automatically)
  - `action_type`: String (e.g., `Kubernetes NetworkPolicy`, `Ansible Node Restart`, `Scale Down`)
  - `target_namespace`: String
  - `updated_by`: ObjectId (Reference to `Users`)
  - `updated_at`: Date
- **Relationships**:
  - Many-to-One with `Users`.
- **Indexes**:
  - `name` (Ascending, Unique)

### 1.5. Collection: Responses
- **Purpose**: Logs execution metrics and latencies of threat remediation actions.
- **Fields**:
  - `_id`: ObjectId (Primary Key)
  - `threat_event_id`: ObjectId (Reference to `ThreatEvents`)
  - `triggered_at`: Date
  - `completed_at`: Date
  - `execution_latency_ms`: Double (Time elapsed during script execution)
  - `action_taken`: String (e.g., `Kubernetes NetworkPolicy applied`)
  - `output_logs`: String (Raw stderr/stdout from runner)
  - `result`: String (e.g., `Success`, `Failed`)
- **Relationships**:
  - One-to-One with `ThreatEvents`.
- **Indexes**:
  - `threat_event_id` (Ascending)
  - `result` (Ascending)

### 1.6. Collection: MonitoringMetrics
- **Purpose**: Aggregates time-series performance data (CPU, memory, packet rates) for dashboard plotting.
- **Fields**:
  - `_id`: ObjectId (Primary Key)
  - `timestamp`: Date
  - `pod_id`: String
  - `cpu_utilization`: Double (Percentage)
  - `memory_utilization`: Double (MB)
  - `packet_rate_in`: Double (packets/sec)
  - `packet_rate_out`: Double (packets/sec)
  - `latency_overhead_ms`: Double
- **Relationships**:
  - None (Independent timeseries metrics data).
- **Indexes**:
  - `timestamp` (Descending)
  - `pod_id` (Ascending)
  - TTL Index on `timestamp` (Expires documents after 7 days to preserve storage)

### 1.7. Collection: Experiments
- **Purpose**: Defines parameters of planned evaluation benchmarks (e.g. comparing algorithms).
- **Fields**:
  - `_id`: ObjectId (Primary Key)
  - `experiment_id`: String (Unique, e.g. `EXP-01`)
  - `title`: String
  - `description`: String
  - `target_metric`: String (e.g., `Detection Latency`)
  - `run_count`: Integer
  - `started_at`: Date
  - `ended_at`: Date
- **Relationships**:
  - One-to-Many with `ResearchResults`.
- **Indexes**:
  - `experiment_id` (Ascending, Unique)

### 1.8. Collection: ResearchResults
- **Purpose**: Records raw metric measurements for each experimental run for thesis compilation.
- **Fields**:
  - `_id`: ObjectId (Primary Key)
  - `experiment_id`: ObjectId (Reference to `Experiments`)
  - `run_number`: Integer
  - `parameters`: Object (e.g., `{ algorithm: 'Autoencoder', dataset: 'CICIDS2018' }`)
  - `measured_value`: Double
  - `unit`: String (e.g., `ms`, `percent`, `MB`)
  - `logged_at`: Date
- **Relationships**:
  - Many-to-One with `Experiments`.
- **Indexes**:
  - `experiment_id` (Ascending)
