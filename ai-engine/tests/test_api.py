from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "OK", "version": "1.0.0"}

def test_api_train_and_predict():
    res_train = client.post("/train", json={"epochs": 2, "batch_size": 4})
    assert res_train.status_code == 200
    assert res_train.json()["status"] == "success"
    
    test_sample = {
        "cpu_utilization": 12.0,
        "memory_usage_percent": 35.5,
        "disk_usage_percent": 25.0,
        "packet_rate_in": 1000,
        "packet_rate_out": 2000
    }
    res_predict = client.post("/predict", json=test_sample)
    assert res_predict.status_code == 200
    assert "is_anomaly" in res_predict.json()
