from fastapi.testclient import TestClient
from src.main import app, evaluate_rules

client = TestClient(app)

def test_cryptography_rules():
    # Test high quantum risk (RSA-2048)
    inputs = {
        "urs": 20.0,
        "decision": "Normal",
        "topContributor": "",
        "anomaly_score": 0.05,
        "reconstruction_error": 0.003,
        "quantumReadiness": {
            "overallQuantumRisk": "Very High"
        }
    }
    recs = evaluate_rules(inputs)
    crypto_recs = [r for r in recs if r["category"] == "Cryptography"]
    assert len(crypto_recs) == 1
    assert crypto_recs[0]["recommendationId"] == "REC-CRYPTO-001"
    assert crypto_recs[0]["priority"] == "Critical"
    assert crypto_recs[0]["estimatedRiskReduction"] == 75.0

def test_resource_threat_rules():
    # Test CPU Spike Crypto Mining threat
    inputs = {
        "urs": 85.0,
        "decision": "Critical",
        "topContributor": "CPU",
        "anomaly_score": 0.95,
        "reconstruction_error": 0.30,
        "attackProfile": "Crypto Mining"
    }
    recs = evaluate_rules(inputs)
    categories = [r["category"] for r in recs]
    assert "Kubernetes" in categories
    assert "Docker" in categories
    assert "Ansible Playbooks" in categories
    assert "Monitoring" in categories
    
    k8s_rec = [r for r in recs if r["category"] == "Kubernetes"][0]
    assert k8s_rec["recommendationId"] == "REC-K8S-001"
    assert k8s_rec["priority"] == "Critical"

def test_container_escape_rules():
    # Test Container Escape Attempt
    inputs = {
        "urs": 90.0,
        "decision": "Critical",
        "topContributor": "CPU",
        "anomaly_score": 0.98,
        "reconstruction_error": 0.45,
        "attackProfile": "Container Escape Attempt"
    }
    recs = evaluate_rules(inputs)
    categories = [r["category"] for r in recs]
    assert "Kubernetes" in categories
    assert "Ansible Playbooks" in categories
    
    esc_rec = [r for r in recs if r["recommendationId"] == "REC-K8S-003"][0]
    assert esc_rec["priority"] == "Critical"
    assert esc_rec["estimatedRiskReduction"] == 90.0
    assert esc_rec["automationSupported"] is True

def test_policy_api_endpoint():
    payload = {
        "urs": 75.0,
        "decision": "Alert",
        "topContributor": "Network",
        "anomaly_score": 0.85,
        "reconstruction_error": 0.15,
        "attackProfile": "Network Flood"
    }
    res = client.post("/policy/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    for rec in data:
        assert "recommendationId" in rec
        assert "title" in rec
        assert "description" in rec
        assert "category" in rec
        assert "priority" in rec
        assert "confidence" in rec
        assert "estimatedRiskReduction" in rec
        assert "automationSupported" in rec
        assert "reasoning" in rec
