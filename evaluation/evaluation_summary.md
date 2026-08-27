# Experimental Evaluation Summary

## Research Metadata
- **Timestamp**: 2026-07-25T13:45:18.965303Z
- **Python Version**: 3.11.9
- **OS Platform**: Windows (AMD64)
- **Configuration Hash**: 6ac9340c96a605d9296b0877a1da07a449b1c3c14baf97b5671f119c20a64071

## Key Findings
1. **Algorithmic Correctness**: Successfully validated all correctness components:
   - Playbook score ranking correctness checked.
   - Playbook deduplication check passed.
   - Mutual exclusions conflict filtering check passed.
   - Kahn topological sorts check passed.
2. **URS Mitigation Effectiveness**: The optimization engine reduced security posture risk by an average of **32.11% URS**, compared to Naive FIFO prioritization.
3. **Execution Latency**: Evaluated optimization execution times with an average speed of **2.39ms**, proving suitability for active network inline deployments.
4. **Reproducibility & Determinism**: Validated 100% deterministic outputs across repeated scenario runs.
