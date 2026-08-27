# Experimental Reproducibility Guide

This guide details steps required to replicate the evaluation outcomes.

---

## 1. Environment Specifications
- **Python Version**: 3.11.9
- **OS Platform**: Windows (AMD64)
- **Git Commit**: e0fbaf2078319d8fdd2f0dd0486ffa0346001194

---

## 2. Integrity Verification Hashes
- **Configuration Hash**: `6ac9340c96a605d9296b0877a1da07a449b1c3c14baf97b5671f119c20a64071`
- **Scenario Hash**: `14027ad49861ece74a4ecb418cc749ac9f27cbb09bbd3c4f460230b88246f66c`
- **Weights Hash**: `e495a5175fbd96193cde106167082d5f8e3dbcdb3015412b4f2fe07e5a05e1b2`

---

## 3. Replication Steps
1. Setup Python virtual environment.
2. Load configuration parameters from `evaluation/evaluation_config.json`.
3. Run the evaluation orchestrator:
   ```bash
   python evaluation/evaluation_runner.py
   ```
4. Verify results inside `evaluation/evaluation_results.json` match identical metrics.
