# E2E Pipeline Validation Report
Generated on: 2026-07-28 07:35:36 UTC

## Summary
- **Total Scenarios**: 7
- **Passed**: 0
- **Failed**: 7
- **Status**: FAILING

## Scenario Execution Details
| Scenario ID | Name | Expected URS | Actual URS | Expected Decision | Actual Decision | Status | Pipeline Latency |
|-------------|------|--------------|------------|-------------------|-----------------|--------|------------------|
| crypto_mining | Crypto Mining Malware | 91.0 | 60.0 | Critical | Monitor | **FAIL** | 12059.4ms |
| data_exfiltration | Data Exfiltration to Threat Actor | 82.0 | 44.6 | Critical | Monitor | **FAIL** | 12308.6ms |
| ddos | DDoS SYN Flood Saturation | 85.0 | 56.2 | Critical | Monitor | **FAIL** | 12998.8ms |
| insider | Insider Threat Action | 40.0 | 44.5 | Alert | Monitor | **FAIL** | 13150.3ms |
| low_risk | Normal Operations / Baseline | 10.5 | 42.1 | Normal | Monitor | **FAIL** | 13083.1ms |
| privilege_escalation | Privilege Escalation Attack | 68.0 | 51.5 | Critical | Monitor | **FAIL** | 12875.3ms |
| ransomware | Ransomware / Volume Encryption | 95.0 | 58.4 | Critical | Monitor | **FAIL** | 12648.7ms |

## Performance Latency Summary
| Service | Average Latency (ms) | Min Latency (ms) | Max Latency (ms) |
|---------|----------------------|------------------|------------------|
| AI | 2059.1ms | 2023.2ms | 2116.3ms |
| RISK | 6402.5ms | 5766.1ms | 6915.1ms |
| PREDICTION | 55.5ms | 24.0ms | 113.4ms |
| POLICY | 2101.3ms | 2090.8ms | 2110.4ms |
| AUTOMATION | 2169.1ms | 2062.3ms | 2611.0ms |
| TOTAL_PIPELINE | 12732.0ms | 12059.4ms | 13150.3ms |

## End of Report
