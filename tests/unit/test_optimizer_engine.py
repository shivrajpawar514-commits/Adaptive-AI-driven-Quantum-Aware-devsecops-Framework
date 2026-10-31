import pytest
import os
import sys

# Ensure automation-engine is on path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "automation-engine"))

from src.optimizer import get_optimizer
from src.playbook_registry import Playbook, PLAYBOOKS_REGISTRY

def test_root_topological_cycle_detection():
    """Verify cycle detection raises ValueError."""
    pb1 = Playbook(id="c1", name="C1", description="C1", supported_findings=["test"], dependencies=["c2"])
    pb2 = Playbook(id="c2", name="C2", description="C2", supported_findings=["test"], dependencies=["c1"])
    opt = get_optimizer("deterministic")
    with pytest.raises(ValueError, match="Cyclic dependency detected"):
        opt.optimize([pb1, pb2], [{"title": "test"}], 80.0)

def test_root_tied_priorities_ordering():
    """Verify tie-breaker preserves alphabetical ID determinism."""
    pb_b = Playbook(id="pb_b", name="B", description="B", supported_findings=["test"], category="CatB", recovery_score=5.0, execution_priority="High")
    pb_a = Playbook(id="pb_a", name="A", description="A", supported_findings=["test"], category="CatA", recovery_score=5.0, execution_priority="High")
    opt = get_optimizer("deterministic")
    res = opt.optimize([pb_b, pb_a], [{"title": "test"}], 50.0)
    ordered_ids = [item["playbookId"] for item in res["executionOrder"]]
    assert ordered_ids == ["pb_a", "pb_b"]

def test_root_deterministic_idempotence():
    """Verify multiple executions yield identical results."""
    findings = [{"title": "crypto malware", "severity": "high"}]
    opt = get_optimizer("deterministic")
    res1 = opt.optimize(PLAYBOOKS_REGISTRY, findings, 70.0)
    res2 = opt.optimize(PLAYBOOKS_REGISTRY, findings, 70.0)
    assert res1["executionOrder"] == res2["executionOrder"]
    assert res1["metrics"] == res2["metrics"]

def test_root_invalid_policy_rejection():
    """Verify invalid policy values raise ValueError."""
    opt = get_optimizer("deterministic")
    with pytest.raises(ValueError, match="Invalid policy parameter"):
        opt.optimize(PLAYBOOKS_REGISTRY, [{"title": "test"}], -10.0)
