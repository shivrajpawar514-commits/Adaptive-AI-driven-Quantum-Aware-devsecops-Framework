import pytest
import random
from fastapi.testclient import TestClient
from src.main import app, db_helper
from src.optimizer import get_optimizer
from src.playbook_registry import Playbook, PLAYBOOKS_REGISTRY

client = TestClient(app)

# -----------------------------------------------------------------------------
# 1. Dependency Cycles Tests
# -----------------------------------------------------------------------------
def test_two_node_dependency_cycle():
    """Verify cycle detection for 2 playbooks (A -> B -> A)."""
    cyclic_playbooks = [
        Playbook(
            id="cycle_pb_a",
            name="Playbook A",
            description="Cycle node A",
            supported_findings=["finding_cycle"],
            dependencies=["cycle_pb_b"],
            category="CycleCatA",
            compatible_cloud="aws",
            recovery_score=8.0,
            disruption_score=2.0,
            execution_priority="High"
        ),
        Playbook(
            id="cycle_pb_b",
            name="Playbook B",
            description="Cycle node B",
            supported_findings=["finding_cycle"],
            dependencies=["cycle_pb_a"],
            category="CycleCatB",
            compatible_cloud="aws",
            recovery_score=8.0,
            disruption_score=2.0,
            execution_priority="High"
        )
    ]
    findings = [{"title": "finding_cycle", "resource": "ec2", "severity": "high"}]
    optimizer = get_optimizer("deterministic")

    with pytest.raises(ValueError, match="Cyclic dependency detected among playbooks"):
        optimizer.optimize(cyclic_playbooks, findings, 75.0)


def test_three_node_dependency_cycle():
    """Verify cycle detection for 3 playbooks (A -> B -> C -> A)."""
    cyclic_playbooks = [
        Playbook(
            id="node_1",
            name="Node 1",
            description="Cycle 1",
            supported_findings=["test_cycle_3"],
            dependencies=["node_2"],
            category="Cat1",
            recovery_score=5.0
        ),
        Playbook(
            id="node_2",
            name="Node 2",
            description="Cycle 2",
            supported_findings=["test_cycle_3"],
            dependencies=["node_3"],
            category="Cat2",
            recovery_score=5.0
        ),
        Playbook(
            id="node_3",
            name="Node 3",
            description="Cycle 3",
            supported_findings=["test_cycle_3"],
            dependencies=["node_1"],
            category="Cat3",
            recovery_score=5.0
        )
    ]
    findings = [{"title": "test_cycle_3", "severity": "medium"}]
    optimizer = get_optimizer("deterministic")

    with pytest.raises(ValueError, match="Cyclic dependency detected"):
        optimizer.optimize(cyclic_playbooks, findings, 60.0)


# -----------------------------------------------------------------------------
# 2. Tied Priorities Deterministic Ordering Tests
# -----------------------------------------------------------------------------
def test_tied_priorities_deterministic_break():
    """Verify that playbooks with identical scores are ordered deterministically by ID."""
    tied_playbooks = [
        Playbook(
            id="pb_zebra",
            name="Zebra Playbook",
            description="Same score Z",
            supported_findings=["finding_tie"],
            category="CatZ",
            recovery_score=6.0,
            disruption_score=3.0,
            estimated_execution_time=5.0,
            confidence=0.8,
            execution_priority="High",
            severity=["high"]
        ),
        Playbook(
            id="pb_alpha",
            name="Alpha Playbook",
            description="Same score A",
            supported_findings=["finding_tie"],
            category="CatA",
            recovery_score=6.0,
            disruption_score=3.0,
            estimated_execution_time=5.0,
            confidence=0.8,
            execution_priority="High",
            severity=["high"]
        ),
        Playbook(
            id="pb_mango",
            name="Mango Playbook",
            description="Same score M",
            supported_findings=["finding_tie"],
            category="CatM",
            recovery_score=6.0,
            disruption_score=3.0,
            estimated_execution_time=5.0,
            confidence=0.8,
            execution_priority="High",
            severity=["high"]
        )
    ]
    findings = [{"title": "finding_tie", "severity": "high"}]
    optimizer = get_optimizer("deterministic")

    # Run in different initial permutations
    for perm in [tied_playbooks, list(reversed(tied_playbooks)), [tied_playbooks[1], tied_playbooks[0], tied_playbooks[2]]]:
        res = optimizer.optimize(perm, findings, 80.0)
        ordered_ids = [item["playbookId"] for item in res["executionOrder"]]
        # Since scores are identical, alphabetical ID order pb_alpha, pb_mango, pb_zebra must be preserved
        assert ordered_ids == ["pb_alpha", "pb_mango", "pb_zebra"]


# -----------------------------------------------------------------------------
# 3. Invalid Policies & Input Validation Tests
# -----------------------------------------------------------------------------
def test_invalid_policy_urs_boundaries():
    """Verify rejection of invalid URS risk scores outside [0.0, 100.0]."""
    optimizer = get_optimizer("deterministic")
    findings = [{"title": "crypto malware", "severity": "high"}]

    with pytest.raises(ValueError, match="Invalid policy parameter: URS score must be between 0.0 and 100.0"):
        optimizer.optimize(PLAYBOOKS_REGISTRY, findings, -5.0)

    with pytest.raises(ValueError, match="Invalid policy parameter: URS score must be between 0.0 and 100.0"):
        optimizer.optimize(PLAYBOOKS_REGISTRY, findings, 150.0)


def test_invalid_playbook_policy_priority():
    """Verify rejection of playbooks configured with unrecognized policy priority."""
    invalid_playbook = Playbook(
        id="invalid_pol_pb",
        name="Invalid Policy PB",
        description="Invalid",
        supported_findings=["test_inv"],
        execution_priority="ULTRA_EXTREME_UNSUPPORTED"
    )
    optimizer = get_optimizer("deterministic")
    with pytest.raises(ValueError, match="Invalid policy priority"):
        optimizer.score_playbook(invalid_playbook, 50.0, "high")


# -----------------------------------------------------------------------------
# 4. Repeated Executions Idempotency Tests
# -----------------------------------------------------------------------------
def test_repeated_executions_idempotence():
    """Verify 50 consecutive optimization runs produce bit-for-bit identical results."""
    findings = [
        {"title": "crypto malware compromise isolate", "resource": "ec2", "severity": "critical"},
        {"title": "Restrict wildcard 0.0.0.0/0 SSH rule", "resource": "security_group", "severity": "high"}
    ]
    optimizer = get_optimizer("deterministic")
    baseline = optimizer.optimize(PLAYBOOKS_REGISTRY, findings, 88.0)

    for _ in range(50):
        run = optimizer.optimize(PLAYBOOKS_REGISTRY, findings, 88.0)
        assert run["metrics"] == baseline["metrics"]
        assert [x["playbookId"] for x in run["executionOrder"]] == [x["playbookId"] for x in baseline["executionOrder"]]
        assert [x["priorityScore"] for x in run["executionOrder"]] == [x["priorityScore"] for x in baseline["executionOrder"]]
        assert run["ursProjection"] == baseline["ursProjection"]


# -----------------------------------------------------------------------------
# 5. Deterministic Ordering under Shuffled Inputs
# -----------------------------------------------------------------------------
def test_deterministic_ordering_under_shuffled_findings():
    """Verify shuffling findings order does not change final execution order."""
    findings_1 = [
        {"title": "crypto malware", "resource": "ec2", "severity": "critical"},
        {"title": "Restrict wildcard 0.0.0.0/0 SSH rule", "resource": "security_group", "severity": "high"}
    ]
    findings_2 = list(reversed(findings_1))

    optimizer = get_optimizer("deterministic")
    res1 = optimizer.optimize(PLAYBOOKS_REGISTRY, findings_1, 90.0)
    res2 = optimizer.optimize(PLAYBOOKS_REGISTRY, findings_2, 90.0)

    order1 = [x["playbookId"] for x in res1["executionOrder"]]
    order2 = [x["playbookId"] for x in res2["executionOrder"]]
    assert order1 == order2


# -----------------------------------------------------------------------------
# 6. Dry-Run Mode Tests
# -----------------------------------------------------------------------------
def test_remediation_dry_run_mode():
    """Verify dry-run mode returns plan and audit trail without live execution status."""
    payload = {
        "riskScore": 92.0,
        "decision": "Critical",
        "recommendations": ["isolate compromised ec2"],
        "instanceId": "i-dryrun-test",
        "dryRun": True,
        "operator": "secops-auditor",
        "operatorRole": "secops"
    }
    res = client.post("/automation/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["dryRun"] is True
    assert data["executionStatus"] == "Dry Run (Simulated)"
    assert "rollbackPlan" in data
    assert len(data["rollbackPlan"]) >= 1


# -----------------------------------------------------------------------------
# 7. Authorization & RBAC Checks
# -----------------------------------------------------------------------------
def test_authorization_check_unauthorized_role():
    """Verify users with untrusted or guest roles are rejected with HTTP 403."""
    payload = {
        "riskScore": 85.0,
        "decision": "High",
        "recommendations": ["isolate ec2"],
        "operator": "unauthorized-guest",
        "operatorRole": "guest"
    }
    res = client.post("/automation/execute", json=payload)
    assert res.status_code == 403
    assert "Authorization check failed" in res.text


def test_authorization_check_invalid_auth_token():
    """Verify invalid auth token is rejected with HTTP 401."""
    payload = {
        "riskScore": 85.0,
        "decision": "High",
        "recommendations": ["isolate ec2"],
        "operatorRole": "secops",
        "authToken": "invalid-token"
    }
    res = client.post("/automation/execute", json=payload)
    assert res.status_code == 401


# -----------------------------------------------------------------------------
# 8. Approval Gates for Critical Remediation
# -----------------------------------------------------------------------------
def test_approval_gate_workflow():
    """Verify critical action (risk >= 90) enters PENDING_APPROVAL and succeeds once approved."""
    payload = {
        "riskScore": 96.0,
        "decision": "Critical",
        "recommendations": ["isolate compromised ec2"],
        "instanceId": "i-critical-target",
        "dryRun": False,
        "operatorRole": "secops",
        "approved": False
    }
    # 1. Submit unapproved critical action
    res = client.post("/automation/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["executionStatus"] == "Pending Approval"
    assert "approvalGate" in data
    assert data["approvalGate"]["required"] is True
    gate_id = data["approvalGate"]["gateId"]

    # 2. Attempt approval with insufficient role -> 403
    bad_approve = {
        "auditId": gate_id,
        "approvedBy": "junior-analyst",
        "approverRole": "operator"
    }
    res_bad = client.post("/automation/approve", json=bad_approve)
    assert res_bad.status_code == 403

    # 3. Approve with SecOps Lead role -> 200
    good_approve = {
        "auditId": gate_id,
        "approvedBy": "alice-secops-lead",
        "approverRole": "secops-lead"
    }
    res_good = client.post("/automation/approve", json=good_approve)
    assert res_good.status_code == 200
    app_data = res_good.json()
    assert app_data["executionStatus"] == "Executed (Simulation Mode)"


# -----------------------------------------------------------------------------
# 9. Structured Rollback Plan & Execution
# -----------------------------------------------------------------------------
def test_structured_rollback_plan_and_execution():
    """Verify execution contains reversible rollback plan and /automation/rollback succeeds."""
    payload = {
        "riskScore": 80.0,
        "decision": "High",
        "recommendations": ["isolate compromised ec2"],
        "instanceId": "i-rollback-ec2",
        "operatorRole": "secops"
    }
    exec_res = client.post("/automation/execute", json=payload)
    assert exec_res.status_code == 200
    data = exec_res.json()
    audit_id = data["auditId"]
    assert "rollbackPlan" in data
    assert len(data["rollbackPlan"]) >= 1

    # Execute rollback
    rb_payload = {"auditId": audit_id, "operator": "secops-lead"}
    rb_res = client.post("/automation/rollback", json=rb_payload)
    assert rb_res.status_code == 200
    rb_data = rb_res.json()
    assert rb_data["status"] == "success"
    assert rb_data["executionStatus"] == "Rolled Back (Simulation Mode)"


# -----------------------------------------------------------------------------
# 10. Audit Trail & Cryptographic Signature Integrity
# -----------------------------------------------------------------------------
def test_audit_trail_and_signature_integrity():
    """Verify audit entries have structured lifecycle trails and tamper-evident SHA-256 signatures."""
    payload = {
        "riskScore": 75.0,
        "decision": "Medium",
        "recommendations": ["isolate compromised ec2"],
        "instanceId": "i-integrity-check",
        "operator": "secops-auditor",
        "operatorRole": "secops"
    }
    res = client.post("/automation/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    audit_id = data["auditId"]

    # Verify audit integrity via endpoint
    verify_res = client.get(f"/automation/audit/verify/{audit_id}")
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["valid"] is True
    assert len(v_data["storedSignature"]) == 64
