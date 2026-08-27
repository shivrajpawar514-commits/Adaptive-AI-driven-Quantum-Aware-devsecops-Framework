# Autonomous DevSecOps Remediation & Automation Engine

The **Automation Engine Microservice** implements the final research contribution of the Adaptive AI-Driven Quantum-Aware DevSecOps Framework: **Closed-Loop Autonomous Incident Response**.

---

## 1. Closed-Loop Architecture

```
Cloud Monitoring (CloudWatch / SysInfo)
          │
          ▼
AI Anomaly Detection (LSTM-Autoencoder)
          │
          ▼
Adaptive URS Risk Engine (Context-Aware)
          │
          ▼
Post-Quantum Cryptographic Posture Audit (QRAE)
          │
          ▼
Intelligent Policy Recommendation Engine (IPRE)
          │
          ▼
Automation Engine (Port 9100 /automation/execute) ◄── [Closed-Loop Remediation]
          │
          ├─► MongoDB Collection: automation_history
          │
          ▼
Frontend React Dashboard (Automation Center Page)
```

---

## 2. Supported Playbook Output Formats (Simulation Mode)

| Playbook Format | Output Type | Primary Remediation Focus |
| :--- | :--- | :--- |
| **AWS CLI** | Command Line | Instance state management, security group ingress revocation, WAF rate limit ACL association |
| **Ansible** | YAML Playbook | Host OS configuration management, Nginx PQC cipher enforcement, container resource limits |
| **Terraform** | HCL Manifest (`.tf`) | Declarative infrastructure state locking, public SSH rule block, EC2 state enforcement |
| **kubectl** | CLI Command | Container pod quarantine labeling, Kubernetes backend deployment scaling |
| **Shell Script** | Bash (`.sh`) | Local multi-tool orchestration combining cloud APIs, kubectl, and rekeying endpoints |
| **JSON Execution Plan**| JSON Object | Structured step-by-step execution metadata for programmatic ingestion |

---

## 3. API Endpoints Matrix

- **`GET /health`**: Microservice health probe. Returns HTTP 200 with service status.
- **`POST /automation/execute`**: Accepts threat context payload (`riskScore`, `decision`, `recommendations`, `provider`, `instanceId`), translates policy recommendations into multi-format playbooks, and records audit trail into MongoDB.
- **`GET /automation/history`**: Returns complete history of remediation runs from MongoDB `automation_history` collection.
- **`POST /automation/rollback`**: Executes simulation rollback for a specific audit record ID (`auditId`).

---

## 4. MongoDB Schema (`automation_history` collection)

```json
{
  "auditId": "AUD-AUTO-1721419200",
  "timestamp": "2026-07-20T12:00:00Z",
  "instanceId": "i-04ba6569c74d41d59",
  "provider": "aws",
  "riskScore": 95.0,
  "decision": "Critical",
  "recommendations": [
    "Scale EC2 instance capacity",
    "Isolate compromised container pod"
  ],
  "executionPlanCount": 5,
  "executionPlan": [
    {
      "type": "AWS CLI",
      "title": "Isolate Compromised EC2 Instance",
      "command": "aws ec2 stop-instances --instance-ids i-04ba6569c74d41d59 --region us-east-1",
      "details": "Gracefully stops target instance to prevent lateral malware movement."
    }
  ],
  "ansiblePlaybook": "---\n- name: Closed-Loop DevSecOps Remediation...",
  "terraformManifest": "provider \"aws\" { ... }",
  "awsCliCommands": ["aws ec2 stop-instances ..."],
  "kubectlCommands": ["kubectl scale deployment ..."],
  "shellScript": "#!/bin/bash\n...",
  "automationLevel": "Fully Automated",
  "estimatedExecutionTime": 5.3,
  "executionStatus": "Executed (Simulation Mode)",
  "rollbackStatus": "Available"
}
```

---

## 5. Local Execution & Testing

```bash
cd automation-engine
pip install -r requirements.txt
python -m uvicorn src.main:app --host 0.0.0.0 --port 9100
```

### Running Unit Tests
```bash
python -m pytest tests
```
*Result*: `6 passed`
