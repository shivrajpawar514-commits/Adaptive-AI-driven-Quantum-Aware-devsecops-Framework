import os
from fastapi.testclient import TestClient
from src.main import app, ATTACK_PROFILES, db_helper

client = TestClient(app)

def test_telemetry_generation():
    # Test that normal workload ranges are respected
    payload = {
        "attackProfile": "Normal Workload",
        "workloadProfile": "Development"
    }
    res = client.post("/simulation/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    assert data["status"] == "success"
    details = data["detail"]
    telemetry = details["telemetry"]
    
    # Check Normal Workload bounds
    cpu_bounds = ATTACK_PROFILES["Normal Workload"]["cpu_usage"]
    assert cpu_bounds[0] <= telemetry["cpu_usage"] <= cpu_bounds[1]
    
    mem_bounds = ATTACK_PROFILES["Normal Workload"]["memory_usage"]
    assert mem_bounds[0] <= telemetry["memory_usage"] <= mem_bounds[1]

def test_simulation_run_detection_and_comparative_result():
    # Test Normal Workload (should have low URS, detected = False)
    payload_normal = {
        "attackProfile": "Normal Workload",
        "workloadProfile": "Development"
    }
    res = client.post("/simulation/run", json=payload_normal)
    assert res.status_code == 200
    res_data = res.json()["results"]
    assert res_data["attackName"] == "Normal Workload"
    assert res_data["detected"] is False
    assert res_data["decision"] == "Normal"
    
    # Test Crypto Mining (should have high URS, detected = True)
    payload_mining = {
        "attackProfile": "Crypto Mining",
        "workloadProfile": "Production"
    }
    res_mining = client.post("/simulation/run", json=payload_mining)
    assert res_mining.status_code == 200
    res_mining_data = res_mining.json()["results"]
    assert res_mining_data["attackName"] == "Crypto Mining"
    assert res_mining_data["detected"] is True
    assert res_mining_data["decision"] != "Normal"

def test_history_and_results_endpoints():
    # Run a few simulations to guarantee records exist
    client.post("/simulation/run", json={"attackProfile": "Normal Workload"})
    client.post("/simulation/run", json={"attackProfile": "CPU Spike"})
    
    # Check history endpoint
    res_hist = client.get("/simulation/history?limit=10")
    assert res_hist.status_code == 200
    hist_data = res_hist.json()
    assert hist_data["status"] == "success"
    assert len(hist_data["data"]) >= 2
    
    # Check results endpoint
    res_results = client.get("/simulation/results?limit=10")
    assert res_results.status_code == 200
    results_data = res_results.json()
    assert results_data["status"] == "success"
    assert len(results_data["data"]) >= 2
    
    # Check results structure
    comp = results_data["data"][0]
    assert "attackName" in comp
    assert "detected" in comp
    assert "latencyMs" in comp
    assert "confidence" in comp
    assert "riskScore" in comp
    assert "decision" in comp
    assert "topContributor" in comp
    assert "quantumReadiness" in comp
    assert "recommendation" in comp
