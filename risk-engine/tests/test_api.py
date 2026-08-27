from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "OK", "version": "1.0.0"}

def test_api_evaluate_and_history():
    payload = {
        "anomaly_score": 0.8,
        "reconstruction_error": 0.05,
        "confidence_score": 0.9,
        "cpu_usage": 85.0,
        "memory_usage": 70.0,
        "disk_usage": 40.0,
        "network_usage": 500000.0
    }
    
    res_eval = client.post("/risk/evaluate", json=payload)
    assert res_eval.status_code == 200
    assert res_eval.json()["status"] == "success"
    assert "urs" in res_eval.json()
    assert "decision" in res_eval.json()
    assert "reason" in res_eval.json()
    
    res_history = client.get("/risk/history")
    assert res_history.status_code == 200
    assert len(res_history.json()["data"]) >= 1
