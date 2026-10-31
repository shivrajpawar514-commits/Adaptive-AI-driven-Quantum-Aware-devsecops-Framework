import pytest
import os
import sys
from fastapi.testclient import TestClient

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "automation-engine"))

from src.main import app

client = TestClient(app)

def test_dry_run_remediation_unit():
    """Verify dry run mode generates plan and rollback without live execution."""
    res = client.post("/automation/execute", json={
        "riskScore": 85.0,
        "decision": "High",
        "recommendations": ["crypto malware"],
        "dryRun": True,
        "operatorRole": "secops"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["dryRun"] is True
    assert data["executionStatus"] == "Dry Run (Simulated)"
    assert "rollbackPlan" in data

def test_authorization_rejection_unit():
    """Verify unauthorized role is rejected with 403."""
    res = client.post("/automation/execute", json={
        "riskScore": 85.0,
        "decision": "High",
        "recommendations": ["crypto malware"],
        "operatorRole": "unauthorized_viewer"
    })
    assert res.status_code == 403

def test_approval_gate_and_approval_flow_unit():
    """Verify approval gate requires secops-lead approval."""
    res = client.post("/automation/execute", json={
        "riskScore": 95.0,
        "decision": "Critical",
        "recommendations": ["crypto malware"],
        "operatorRole": "secops",
        "approved": False
    })
    assert res.status_code == 200
    data = res.json()
    assert data["executionStatus"] == "Pending Approval"
    gate_id = data["approvalGate"]["gateId"]

    # Approve
    res_app = client.post("/automation/approve", json={
        "auditId": gate_id,
        "approvedBy": "lead-secops",
        "approverRole": "secops-lead"
    })
    assert res_app.status_code == 200
    assert res_app.json()["executionStatus"] == "Executed (Simulation Mode)"
