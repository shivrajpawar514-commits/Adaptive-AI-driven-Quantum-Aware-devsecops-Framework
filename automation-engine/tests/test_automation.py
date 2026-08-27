from fastapi.testclient import TestClient
from src.main import app, db_helper, action_generator

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Automation Engine"

def test_automation_execute_endpoint():
    payload = {
        "riskScore": 95.0,
        "decision": "Critical",
        "recommendations": ["Scale EC2 instance capacity", "Isolate compromised container pod"],
        "provider": "aws",
        "instanceId": "i-04ba6569c74d41d59"
    }
    res = client.post("/automation/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["executionPlan"]) >= 1
    assert data["automationLevel"] == "Fully Automated"
    assert data["rollbackAvailable"] is True
    assert "auditId" in data

def test_playbook_generation():
    plan = action_generator.generate_plan(
        risk_score=92.0,
        decision="Critical",
        recommendations=["Restrict wildcard 0.0.0.0/0 SSH rule"],
        provider="aws",
        instance_id="i-04ba6569c74d41d59"
    )
    assert "ansiblePlaybook" in plan
    assert "terraformManifest" in plan
    assert "awsCliCommands" in plan
    assert "kubectlCommands" in plan
    assert "shellScript" in plan
    assert "jsonPlan" in plan
    assert len(plan["awsCliCommands"]) > 0

def test_audit_logging():
    audit_doc = {
        "auditId": "AUD-TEST-001",
        "instanceId": "i-04ba6569c74d41d59",
        "riskScore": 88.0,
        "decision": "Alert",
        "recommendations": ["Apply rate limiting WAF rule"]
    }
    saved_id = db_helper.save_execution(audit_doc)
    assert saved_id == "AUD-TEST-001"
    
    history = db_helper.get_history()
    assert len(history) > 0

def test_automation_history_endpoint():
    res = client.get("/automation/history")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "data" in data
    assert isinstance(data["data"], list)

def test_rollback_endpoint():
    payload = {"auditId": "AUD-AUTO-9001"}
    res = client.post("/automation/rollback", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["auditId"] == "AUD-AUTO-9001"
    assert "Rolled Back" in data["executionStatus"]
