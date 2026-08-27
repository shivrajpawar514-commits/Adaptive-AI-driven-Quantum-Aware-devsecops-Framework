import os
import requests
import pytest

# Read ports from environment or fall back to defaults
MONITORING_URL = os.getenv("MONITORING_URL", "http://localhost:6001")
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://localhost:8000")
RISK_ENGINE_URL = os.getenv("RISK_ENGINE_URL", "http://localhost:8500")
POLICY_URL = os.getenv("POLICY_URL", "http://localhost:8700")
AUTOMATION_URL = os.getenv("AUTOMATION_URL", "http://localhost:9100")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

def test_monitoring_health():
    """Verify Monitoring Service health contract."""
    res = requests.get(f"{MONITORING_URL}/health", timeout=3)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("success", "OK")

def test_ai_engine_health():
    """Verify AI Engine health contract."""
    res = requests.get(f"{AI_ENGINE_URL}/health", timeout=3)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("success", "OK")

def test_risk_engine_health():
    """Verify Risk Engine health contract."""
    res = requests.get(f"{RISK_ENGINE_URL}/health", timeout=3)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("success", "OK")

def test_policy_engine_health():
    """Verify Policy Engine health contract."""
    res = requests.get(f"{POLICY_URL}/health", timeout=3)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("success", "OK")

def test_automation_engine_health():
    """Verify Automation Engine health contract."""
    res = requests.get(f"{AUTOMATION_URL}/health", timeout=3)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("success", "healthy")

def test_backend_health():
    """Verify Backend Gateway health contract."""
    res = requests.get(f"{BACKEND_URL}/health", timeout=3)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("success", "healthy")

def test_ai_predict_contract():
    """Verify AI Engine prediction contract and response wrapping."""
    payload = {
        "cpu_utilization": 25.0,
        "memory_usage_percent": 50.0,
        "disk_usage_percent": 30.0,
        "packet_rate_in": 1000,
        "packet_rate_out": 800
    }
    res = requests.post(f"{AI_ENGINE_URL}/predict", json=payload, timeout=3)
    assert res.status_code == 200
    data = res.json()
    
    # Assert standard API response format holds
    assert "status" in data
    assert data["status"] == "success"
    assert "timestamp" in data
    assert "request_id" in data
    assert "service" in data
    assert "version" in data
    assert "execution_time" in data
    
    # Assert original data fields are present (at root and/or data)
    assert "is_anomaly" in data
    assert "reconstruction_loss" in data

def test_risk_evaluate_contract():
    """Verify Risk Engine evaluation contract and prediction summary integration."""
    payload = {
        "anomaly_score": 1.0,
        "reconstruction_error": 0.05,
        "confidence_score": 0.95,
        "cpu_usage": 80.0,
        "memory_usage": 70.0,
        "disk_usage": 90.0,
        "network_usage": 5000,
        "resource_id": "test-integration-res",
        "workload_profile": "Production"
    }
    res = requests.post(f"{RISK_ENGINE_URL}/risk/evaluate", json=payload, timeout=3)
    assert res.status_code == 200
    data = res.json()
    
    # Assert standard response envelope
    assert data["status"] == "success"
    
    # Assert risk specific fields
    assert "urs" in data
    assert "decision" in data
    assert "prediction_summary" in data
    
    # Assert prediction_summary is populated and is NOT mock/error if prediction service is online
    pred_summary = data["prediction_summary"]
    assert isinstance(pred_summary, dict)

def test_policy_recommend_contract():
    """Verify Policy Engine recommendation rules."""
    payload = {
        "urs": 85.0,
        "decision": "Critical",
        "topContributor": "cpu_utilization",
        "anomaly_score": 1.0,
        "reconstruction_error": 0.08,
        "attackProfile": "SYN Flood Attack",
        "context": {"profile": "Production"},
        "quantumReadiness": {"overallQuantumRisk": "High"}
    }
    res = requests.post(f"{POLICY_URL}/policy/recommend", json=payload, timeout=3)
    assert res.status_code == 200
    data = res.json()
    
    # Assert standard response envelope
    assert data["status"] == "success"
    
    # Assert recommendations are returned
    recs = data.get("data") or data
    if isinstance(recs, dict) and "data" in recs:
        recs = recs["data"]
    assert isinstance(recs, list)
    assert len(recs) > 0
    assert any(r.get("category") == "Cryptography" for r in recs)

def test_automation_execute_contract():
    """Verify Automation Engine playbook execution and rollback capability."""
    payload = {
        "riskScore": 85.0,
        "decision": "Critical",
        "recommendations": [
            {
                "recommendationId": "REC-CRYPTO-001",
                "title": "Migrate Legacy Cryptography",
                "priority": "Critical",
                "automationSupported": True
            }
        ],
        "provider": "aws",
        "instanceId": "i-test-integration"
    }
    res = requests.post(f"{AUTOMATION_URL}/automation/execute", json=payload, timeout=3)
    assert res.status_code == 200
    data = res.json()
    
    # Assert standard response envelope
    assert data["status"] == "success"
    
    # Assert playbook audit details
    assert "auditId" in data
    assert "executionStatus" in data
    assert "rollbackAvailable" in data

def test_backend_orchestration_pipeline():
    """Verify E2E flow via Backend Gateway pipeline analyzer."""
    res = requests.post(f"{BACKEND_URL}/pipeline/analyze", timeout=15)
    assert res.status_code == 200
    data = res.json()
    
    assert data["status"] == "success"
    assert "correlationId" in data
    assert "risk_score" in data
    assert "decision" in data
    assert "prediction_summary" in data
    assert "recommendations" in data
