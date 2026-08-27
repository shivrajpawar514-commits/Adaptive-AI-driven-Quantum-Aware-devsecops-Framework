# Component & Microservice Architecture Overview

This document reviews the components in the Playbook Optimization SOAR stack.

---

## 1. Request Lifecycle Flow
1. **Detection Input**: Monitoring services discover security anomaly alerts.
2. **Analysis Pass**: Anomaly alerts ingest into Risk, Policy, and Automation Engines.
3. **Prioritization**: `DeterministicPlaybookOptimizer` computes priority scores, deduplicates category overlays, resolves conflicts, and applies Kahn topological sorting.
4. **Execution**: The orchestrator triggers boto3 CLI actions or quarantined pod actions.

---

## 2. Optimization Layer Design
The optimizer is fully decoupled:
- `BaseOptimizer`: Core abstract interface class.
- `DeterministicPlaybookOptimizer`: Concrete strategy pattern scoring instance.
