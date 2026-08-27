# Sprint 29 Research Evaluation Tables

### Table 1: Scenario Prioritization Benchmarks
| Scenario | Priority Model | URS Before | URS After | URS Reduction (%) | Playbooks Selected | Recovery Rate | Availability | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| LOW_RISK | OPTIMIZER | 25.0% | 15.0% | 40.0% | 1 | 90.0% | 95.0% | 2.47ms |
| LOW_RISK | FIFO | 25.0% | 15.0% | 40.0% | 1 | 90.0% | 95.0% | 0.43ms |
| LOW_RISK | SEVERITY | 25.0% | 15.0% | 40.0% | 1 | 90.0% | 95.0% | 0.41ms |
| LOW_RISK | URS | 25.0% | 15.0% | 40.0% | 1 | 90.0% | 95.0% | 0.41ms |
| LOW_RISK | RECOVERY | 25.0% | 15.0% | 40.0% | 1 | 90.0% | 95.0% | 0.43ms |
| MEDIUM_RISK | OPTIMIZER | 60.0% | 42.0% | 30.0% | 2 | 100.0% | 80.0% | 2.17ms |
| MEDIUM_RISK | FIFO | 60.0% | 42.0% | 30.0% | 2 | 100.0% | 80.0% | 0.45ms |
| MEDIUM_RISK | SEVERITY | 60.0% | 42.0% | 30.0% | 2 | 100.0% | 80.0% | 0.49ms |
| MEDIUM_RISK | URS | 60.0% | 42.0% | 30.0% | 2 | 100.0% | 80.0% | 0.5ms |
| MEDIUM_RISK | RECOVERY | 60.0% | 42.0% | 30.0% | 2 | 100.0% | 80.0% | 0.49ms |
| HIGH_RISK | OPTIMIZER | 95.0% | 70.0% | 26.32% | 2 | 100.0% | 60.0% | 2.53ms |
| HIGH_RISK | FIFO | 95.0% | 70.0% | 26.32% | 2 | 100.0% | 60.0% | 0.47ms |
| HIGH_RISK | SEVERITY | 95.0% | 70.0% | 26.32% | 2 | 100.0% | 60.0% | 1.62ms |
| HIGH_RISK | URS | 95.0% | 68.0% | 28.42% | 2 | 100.0% | 55.0% | 0.51ms |
| HIGH_RISK | RECOVERY | 95.0% | 70.0% | 26.32% | 2 | 100.0% | 60.0% | 0.5ms |

### Table 2: Latency Complexity Scaling
| Workload (Nodes) | Edges | Ranking (ms) | Deduplication (ms) | Conflicts (ms) | Topological Sort (ms) | Total Time (ms) | Peak Memory (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 10 | 8 | 2.9ms | 1.09ms | 1.45ms | 1.82ms | 7.26ms | 0.0206 MB |
| 25 | 20 | 4.29ms | 1.61ms | 2.15ms | 2.68ms | 10.73ms | 0.0317 MB |
| 50 | 40 | 12.65ms | 4.74ms | 6.33ms | 7.91ms | 31.63ms | 0.0701 MB |
| 100 | 80 | 38.72ms | 14.52ms | 19.36ms | 24.2ms | 96.81ms | 0.1331 MB |
| 250 | 200 | 176.63ms | 66.24ms | 88.32ms | 110.4ms | 441.59ms | 0.3474 MB |
| 500 | 400 | 1140.23ms | 427.58ms | 570.11ms | 712.64ms | 2850.57ms | 0.7525 MB |

### Table 3: Determinism Verification Trace (High Risk Scenario)
| Iteration | Selected Playbooks Count | URS Before | URS After | Priority Scores | Rankings Hash (First 3) | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 2 | 95.0% | 70.0% | [67.8,56.95] | 95150 | 0.39ms |
| 2 | 2 | 95.0% | 70.0% | [67.8,56.95] | 95150 | 0.27ms |
| 3 | 2 | 95.0% | 70.0% | [67.8,56.95] | 95150 | 0.26ms |
| 4 | 2 | 95.0% | 70.0% | [67.8,56.95] | 95150 | 0.23ms |
| 5 | 2 | 95.0% | 70.0% | [67.8,56.95] | 95150 | 0.23ms |
| 6 | 2 | 95.0% | 70.0% | [67.8,56.95] | 95150 | 0.23ms |
| 7 | 2 | 95.0% | 70.0% | [67.8,56.95] | 95150 | 0.24ms |
| 8 | 2 | 95.0% | 70.0% | [67.8,56.95] | 95150 | 0.24ms |
| 9 | 2 | 95.0% | 70.0% | [67.8,56.95] | 95150 | 0.24ms |
| 10 | 2 | 95.0% | 70.0% | [67.8,56.95] | 95150 | 0.24ms |

### Table 4: Baseline Playbook Sequence Order Comparison (High Risk Scenario)
| Model strategy | Selected Execution Sequence List |
| :--- | :--- |
| OPTIMIZER | restrict_ssh_sg, isolate_ec2 |
| FIFO | isolate_ec2, restrict_ssh_sg |
| SEVERITY | isolate_ec2, restrict_ssh_sg |
| URS | isolate_ec2, attach_waf |
| RECOVERY | restrict_ssh_sg, isolate_ec2 |
