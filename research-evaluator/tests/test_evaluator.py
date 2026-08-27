from fastapi.testclient import TestClient
from src.main import app, db_helper, run_evaluation_metrics

client = TestClient(app)

def test_evaluation_run_math():
    results = run_evaluation_metrics()
    assert "kpis" in results
    assert "comparison" in results
    assert "charts" in results
    
    # Check KPIs format
    k = results["kpis"]
    assert "detectionAccuracy" in k
    assert "detectionLatencyMs" in k
    assert "falsePositiveEstimate" in k
    assert "falseNegativeEstimate" in k
    assert "quantumReadinessAverage" in k
    assert k["detectionAccuracy"] > 80.0
    
    # Check Comparison format
    c = results["comparison"]
    assert "headers" in c
    assert "rows" in c
    assert len(c["rows"]) == 8

def test_evaluation_charts_format():
    results = run_evaluation_metrics()
    ch = results["charts"]
    assert "barChart" in ch
    assert "pieChart" in ch
    assert "radarChart" in ch
    assert "lineChart" in ch
    assert "heatmap" in ch
    assert "riskTrendGraph" in ch
    
    assert ch["barChart"]["title"] == "Detection Latency by Attack Profile"
    assert len(ch["radarChart"]["datasets"]) == 3

def test_api_endpoints():
    # Run evaluation
    res_run = client.post("/evaluation/run")
    assert res_run.status_code == 200
    assert res_run.json()["status"] == "success"
    
    # Get summary
    res_sum = client.get("/evaluation/summary")
    assert res_sum.status_code == 200
    assert "detectionAccuracy" in res_sum.json()["data"]
    
    # Get attacks
    res_att = client.get("/evaluation/attacks")
    assert res_att.status_code == 200
    assert "Normal Workload" in res_att.json()["data"]
    
    # Get comparison
    res_comp = client.get("/evaluation/comparison")
    assert res_comp.status_code == 200
    assert len(res_comp.json()["data"]["rows"]) == 8
    
    # Get dashboard
    res_dash = client.get("/evaluation/dashboard")
    assert res_dash.status_code == 200
    assert "kpis" in res_dash.json()
    assert "charts" in res_dash.json()
