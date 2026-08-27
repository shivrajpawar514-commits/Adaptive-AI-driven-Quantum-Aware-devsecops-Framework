from fastapi.testclient import TestClient
from src.api.main import app
from src.quantum.readiness_engine import QuantumReadinessEngine

client = TestClient(app)

def test_algorithm_lookup_and_score_calculation():
    engine = QuantumReadinessEngine()
    
    # Test ML-KEM Kyber alone
    res = engine.evaluate_posture(["ML-KEM (Kyber)"])
    assert res["quantumReadiness"]["score"] == 95
    assert res["quantumReadiness"]["classification"] == "Excellent"
    assert res["quantumReadiness"]["migrationPriority"] == "Completed"
    assert res["quantumReadiness"]["overallQuantumRisk"] == "Low"
    
    # Test RSA-2048 alone
    res = engine.evaluate_posture(["RSA-2048"])
    assert res["quantumReadiness"]["score"] == 15
    assert res["quantumReadiness"]["classification"] == "Poor"
    assert res["quantumReadiness"]["migrationPriority"] == "Immediate"
    assert res["quantumReadiness"]["overallQuantumRisk"] == "Very High"
    
    # Test mixed: ML-KEM (95) and RSA-2048 (15) -> Average (95 + 15)/2 = 55
    res = engine.evaluate_posture(["ML-KEM (Kyber)", "RSA-2048"])
    assert res["quantumReadiness"]["score"] == 55
    assert res["quantumReadiness"]["classification"] == "Good"
    # Overall risk and migration priority follows the weakest link (RSA-2048)
    assert res["quantumReadiness"]["overallQuantumRisk"] == "Very High"
    assert res["quantumReadiness"]["migrationPriority"] == "Immediate"

def test_classification_logic():
    engine = QuantumReadinessEngine()
    
    # Poor classification (score <= 25)
    res = engine.evaluate_posture(["RSA-2048"])
    assert res["quantumReadiness"]["classification"] == "Poor"
    
    # Moderate classification (26 <= score <= 50)
    res = engine.evaluate_posture(["RSA-2048", "Ed25519"]) # (15 + 65)/2 = 40
    assert res["quantumReadiness"]["score"] == 40
    assert res["quantumReadiness"]["classification"] == "Moderate"
    
    # Good classification (51 <= score <= 75)
    res = engine.evaluate_posture(["ECC P-256"]) # 55
    assert res["quantumReadiness"]["classification"] == "Good"
    
    # Excellent classification (76 <= score <= 100)
    res = engine.evaluate_posture(["ML-KEM (Kyber)"]) # 95
    assert res["quantumReadiness"]["classification"] == "Excellent"

def test_api_schema_and_explainability():
    payload = {
        "anomaly_score": 0.8,
        "reconstruction_error": 0.05,
        "confidence_score": 0.9,
        "cpu_usage": 85.0,
        "memory_usage": 70.0,
        "disk_usage": 40.0,
        "network_usage": 500000.0,
        "timestamp": "2026-07-20T10:00:00Z",
        "cryptography": ["RSA-2048", "ML-KEM (Kyber)"]
    }
    
    res = client.post("/risk/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    # Verify top-level structures exist
    assert "quantumReadiness" in data
    assert "cryptography" in data
    assert "quantumExplanation" in data
    assert "dashboardData" in data
    
    # Validate quantumReadiness fields (Phase 4)
    qr = data["quantumReadiness"]
    assert qr["score"] == 55
    assert qr["classification"] == "Good"
    assert qr["migrationPriority"] == "Immediate"
    assert qr["overallQuantumRisk"] == "Very High"
    
    # Validate cryptography explanations (Phase 5)
    crypto_list = data["cryptography"]
    assert len(crypto_list) == 2
    for item in crypto_list:
        assert "algorithm" in item
        assert "quantumRisk" in item
        assert "readinessWeight" in item
        assert "recommendation" in item
        assert "reason" in item
        
    assert crypto_list[0]["algorithm"] == "RSA-2048"
    assert crypto_list[0]["quantumRisk"] == "Very High"
    
    # Validate human readable summary explanation
    assert "Monitored assets" in data["quantumExplanation"]
    assert "Very High" in data["quantumExplanation"]
    
    # Validate Dashboard fields (Phase 6)
    db = data["dashboardData"]
    # Check camelCase
    assert db["migrationPriority"] == "Immediate"
    assert db["topRecommendation"] == "Migrate to ML-KEM (Kyber) hybrid TLS."
    assert db["highestQuantumRiskAlgorithm"] == "RSA-2048"
    assert db["overallQuantumReadiness"] == "Good"
    # Check exact PascalCase/spaces
    assert db["Migration Priority"] == "Immediate"
    assert db["Top Recommendation"] == "Migrate to ML-KEM (Kyber) hybrid TLS."
    assert db["Highest Quantum Risk Algorithm"] == "RSA-2048"
    assert db["Overall Quantum Readiness"] == "Good"

def test_qrae_backward_compatibility():
    # Payload omitting cryptography lists
    payload = {
        "anomaly_score": 0.5,
        "reconstruction_error": 0.1,
        "confidence_score": 0.8,
        "cpu_usage": 50.0,
        "memory_usage": 50.0,
        "disk_usage": 10.0,
        "network_usage": 100000.0
    }
    
    res = client.post("/risk/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    # Check that it defaulted to legacy baseline (RSA-2048 and ECC P-256)
    assert "quantumReadiness" in data
    assert data["quantumReadiness"]["score"] == 35 # (15 + 55)/2 = 35
    assert data["quantumReadiness"]["classification"] == "Moderate"
    
    # Standard output checks
    assert "urs" in data
    assert "status" in data
    assert "decision" in data
