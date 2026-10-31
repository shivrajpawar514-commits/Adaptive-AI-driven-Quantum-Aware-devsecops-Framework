# Empirical Benchmark Report: Deterministic Playbook Optimizer vs. Naive Baseline

**Generated**: 2026-10-31T18:44:38Z  
**Evaluation Sample**: 1000 Monte Carlo iterations  
**Test Environment**: Python 3.11.15 on darwin

---

## 1. Executive Summary

This empirical evaluation measures the effectiveness, reliability, and computational efficiency of the **Deterministic Playbook Optimization Engine** against a standard single-factor **Naive Greedy Baseline**. 

Across 1000 iterations:
- **Dependency Violations**: The baseline produced 1 invalid dependency ordering(s) (scheduling child tasks prior to prerequisite completion). The Deterministic Optimizer achieved **0 dependency violations (100% topological correctness)** via Kahn's algorithm.
- **Mutual Exclusion Conflicts**: The baseline scheduled 1 conflicting playbooks concurrently. The Deterministic Optimizer resolved 100% of mutual exclusion constraints.
- **Remediation Time Saved**: Deduplication and conflict elimination decreased overall execution duration from **34.0s to 7.0s (79.41% reduction)**.
- **Service Availability**: Disruption penalty weighting preserved service availability at **82.5%** compared to 42.5% in the unpenalized baseline.
- **Reproducibility**: The optimizer demonstrated **zero variance (0.000000000)** across all 1000 runs.

---

## 2. Quantitative Benchmark Results

| Metric | Naive Greedy Baseline | Deterministic Optimizer | Advantage / Delta |
| :--- | :--- | :--- | :--- |
| **Topological Dependency Ordering** | 1 Violations (Broken) | **0 Violations (100% Valid)** | 100% Precedence Guarantee |
| **Conflict Collisions** | 1 Active Collision | **0 Collisions (Resolved)** | 100% Mutual Exclusion |
| **Playbooks Scheduled** | 4 (Includes redundant) | **2 (Deduplicated)** | Category Pruning Active |
| **Total Remediation Duration** | 34.0 seconds | **7.0 seconds** | **79.41% time saved** |
| **Disruption Score** | 11.5 points | **3.5 points** | **69.57% less disruption** |
| **Estimated Service Availability** | 42.5% | **82.5%** | +40.0% availability |
| **Mean Execution Latency** | 0.0041 ms | **0.0201 ms** | Sub-millisecond overhead |
| **P95 Latency** | 0.0043 ms | **0.0215 ms** | Real-time capable (< 1 ms) |
| **Score Variance (1000 runs)** | N/A | **0.000000000** | **100% Deterministic** |

---

## 3. Algorithm Verification

### 3.1 Kahn's Algorithm Topological Precedence
The baseline ranks candidates by raw recovery score, causing `pb_kill_miner_process` (score 9.0) to execute before its prerequisite `pb_quarantine_net` (score 7.0), failing in production because the process immediately respawns over the unquarantined network tunnel.
The **Deterministic Optimizer** correctly constructs an in-degree adjacency graph and evaluates:
1. `pb_quarantine_net` (Stage 1: In-degree = 0)
2. `pb_kill_miner_process` (Stage 2: In-degree decreases to 0)

### 3.2 Category Deduplication & Conflict Filtering
The baseline concurrently selected `pb_kill_miner_process` and `pb_snapshot_live` despite an explicit conflict, and selected `pb_block_port_only` despite `pb_quarantine_net` already isolating the network category.
The **Deterministic Optimizer** automatically pruned `pb_block_port_only` as redundant and rejected `pb_snapshot_live` due to active conflict.

---

## 4. How to Reproduce
Run the benchmark directly from the workspace root:
```bash
python scripts/benchmark_optimizer.py
```
Or execute the automated benchmark test suite:
```bash
pytest tests/unit/test_optimizer_engine.py
```
