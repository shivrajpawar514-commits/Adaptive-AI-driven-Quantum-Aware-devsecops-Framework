import pytest
from fastapi.testclient import TestClient
from src.main import app, db_helper
from src.optimizer import get_optimizer
from src.playbook_registry import PLAYBOOKS_REGISTRY, Playbook

client = TestClient(app)

def test_optimize_endpoint_high_risk():
    payload = {
        "riskScore": 95.0,
        "decision": "Critical",
        "recommendations": [
            "crypto malware compromise isolate",
            "Restrict wildcard 0.0.0.0/0 SSH rule"
        ],
        "provider": "aws",
        "instanceId": "i-04ba6569c74d41d59"
    }
    res = client.post("/automation/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "executionOrder" in data
    assert "ursBefore" in data
    assert "ursAfter" in data
    
    # Check metrics
    metrics = data["metrics"]
    assert metrics["playbooksConsidered"] >= 1
    assert metrics["playbooksSelected"] >= 1
    assert data["ursBefore"] == 95.0
    assert data["ursAfter"] < 95.0

def test_optimize_endpoint_no_matches():
    payload = {
        "riskScore": 20.0,
        "decision": "Low",
        "recommendations": ["Unrelated finding that matches nothing"],
        "provider": "aws"
    }
    res = client.post("/automation/optimize", json=payload)
    # The endpoint raises 404 when no compatible playbooks are found
    assert res.status_code == 404

def test_determinism():
    # Setup test inputs
    findings = [
        {"title": "crypto malware compromise isolate", "resource": "ec2", "severity": "critical"},
        {"title": "Restrict wildcard 0.0.0.0/0 SSH rule", "resource": "security_group", "severity": "high"}
    ]
    current_urs = 88.0

    optimizer = get_optimizer("deterministic")

    # Execute optimizer multiple times
    res1 = optimizer.optimize(PLAYBOOKS_REGISTRY, findings, current_urs)
    res2 = optimizer.optimize(PLAYBOOKS_REGISTRY, findings, current_urs)
    res3 = optimizer.optimize(PLAYBOOKS_REGISTRY, findings, current_urs)

    # Verify identical priority scores
    scores1 = [item["priorityScore"] for item in res1["executionOrder"]]
    scores2 = [item["priorityScore"] for item in res2["executionOrder"]]
    scores3 = [item["priorityScore"] for item in res3["executionOrder"]]
    assert scores1 == scores2 == scores3

    # Verify identical playbook rankings
    ids1 = [item["playbookId"] for item in res1["executionOrder"]]
    ids2 = [item["playbookId"] for item in res2["executionOrder"]]
    ids3 = [item["playbookId"] for item in res3["executionOrder"]]
    assert ids1 == ids2 == ids3

    # Verify identical metrics
    assert res1["metrics"] == res2["metrics"] == res3["metrics"]

    # Verify identical explainability output
    why1 = [item["selectedBecause"] for item in res1["executionOrder"]]
    why2 = [item["selectedBecause"] for item in res2["executionOrder"]]
    assert why1 == why2

def test_deduplication():
    # Setup multiple findings that resolve to the same category
    findings = [
        {"title": "crypto malware", "resource": "ec2", "severity": "critical"},
        {"title": "isolate compromised ec2", "resource": "ec2", "severity": "critical"}
    ]
    optimizer = get_optimizer("deterministic")
    res = optimizer.optimize(PLAYBOOKS_REGISTRY, findings, 90.0)

    # Check that they deduplicate to 1 playbook execution
    ec2_playbooks = [item for item in res["executionOrder"] if item["category"] == "Isolation"]
    assert len(ec2_playbooks) == 1

def test_dependency_resolution():
    # Verify dependency resolution adds dependent playbooks
    # Let's mock a registry where a playbook has a dependency
    test_playbooks = [
        Playbook(
            id="child_pb",
            name="Child Playbook",
            description="Depends on parent",
            supported_findings=["finding_b"],
            dependencies=["parent_pb"],
            category="Test",
            compatible_cloud="aws",
            rollback_supported=True,
            recovery_score=5.0,
            disruption_score=1.0,
            execution_priority="High"
        ),
        Playbook(
            id="parent_pb",
            name="Parent Playbook",
            description="Prerequisite",
            supported_findings=["finding_a"],
            dependencies=[],
            category="Test-Parent",
            compatible_cloud="aws",
            rollback_supported=True,
            recovery_score=5.0,
            disruption_score=1.0,
            execution_priority="Medium"
        )
    ]
    
    findings = [{"title": "finding_b", "resource": "ec2", "severity": "high"}]
    optimizer = get_optimizer("deterministic")
    res = optimizer.optimize(test_playbooks, findings, 80.0)

    # Even though only finding_b was reported, parent_pb should be pulled in by dependency
    pb_ids = [item["playbookId"] for item in res["executionOrder"]]
    assert "parent_pb" in pb_ids
    assert "child_pb" in pb_ids
    
    # Parent must execute first
    parent_index = pb_ids.index("parent_pb")
    child_index = pb_ids.index("child_pb")
    assert parent_index < child_index

def test_conflict_resolution():
    # Setup playbooks with mutual conflicts
    test_playbooks = [
        Playbook(
            id="pb_a",
            name="Playbook A",
            description="Conflict playbook A",
            supported_findings=["finding_x"],
            conflicts=["pb_b"],
            category="CatA",
            compatible_cloud="aws",
            rollback_supported=True,
            recovery_score=8.0, # higher recovery, scores higher
            disruption_score=1.0,
            execution_priority="High"
        ),
        Playbook(
            id="pb_b",
            name="Playbook B",
            description="Conflict playbook B",
            supported_findings=["finding_x"],
            conflicts=["pb_a"],
            category="CatB", # different categories to bypass deduplication
            compatible_cloud="aws",
            rollback_supported=True,
            recovery_score=2.0,
            disruption_score=5.0,
            execution_priority="Low"
        )
    ]

    findings = [{"title": "finding_x", "resource": "ec2", "severity": "high"}]
    optimizer = get_optimizer("deterministic")
    res = optimizer.optimize(test_playbooks, findings, 80.0)

    # Only one of them should run
    pb_ids = [item["playbookId"] for item in res["executionOrder"]]
    assert ("pb_a" in pb_ids) != ("pb_b" in pb_ids) # XOR check
    # pb_a should be chosen because it has higher score
    assert "pb_a" in pb_ids
