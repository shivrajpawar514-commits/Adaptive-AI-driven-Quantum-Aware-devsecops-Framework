# Startup Performance Baseline Report

Generated at: 2026-07-24 15:38:06

## 1. Python Library Import Profiling

| Library | Import Time (seconds) |
|---|---|
| `torch` | 18.158s |
| `pandas` | 4.378s |
| `sklearn` | 8.016s |
| `pymongo` | 0.465s |
| `fastapi` | 0.984s |
| `uvicorn` | 0.289s |

## 2. Microservice Startup Measurements

| Service | Port | Process Launch Time | Time until Port Active | Time until Health Responds | Total Ready Time |
|---|---|---|---|---|---|
| Backend Gateway | 5000 | 0.032s | 5.71s | 6.19s | 6.19s |
| Monitoring Service | 6001 | 0.000s | 5.39s | N/A | 25.00s |
| Cloud Adapter | 7000 | 0.031s | 2.34s | 5.33s | 5.33s |
| AI Engine | 8000 | 0.031s | 8.03s | 8.48s | 8.48s |
| Risk Engine | 8500 | 0.020s | 3.14s | 3.63s | 3.63s |
| Policy Engine | 8700 | 0.033s | 1.95s | 2.55s | 2.55s |
| Research Evaluator | 8800 | 0.031s | 1.70s | 2.13s | 2.13s |
| Digital Twin | 8900 | 0.020s | 2.09s | 2.57s | 2.57s |
| Automation Engine | 9100 | 0.019s | 2.52s | 3.02s | 3.02s |
| Attack Simulator | 8600 | 0.018s | 3.15s | 3.87s | 3.87s |
| Dashboard UI | 5173 | 0.000s | N/A | N/A | 25.00s |

## 3. Key Startup Bottlenecks Identified

- **Sequential Service Spawning**: Services are started one-by-one in the orchestrator, wait for each health check sequentially, causing a cumulative wait time.
- **Blocking Retries & Dependency Installs**: If health check fails on first attempt due to slow startup, orchestrator blocks for package installation.
- **Shared Logging File Locks**: Multi-process Winston logging writing to identical file paths in Node services causes file write lock delays.
