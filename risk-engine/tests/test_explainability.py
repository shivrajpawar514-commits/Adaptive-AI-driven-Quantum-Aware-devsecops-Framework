from fastapi.testclient import TestClient
from src.api.main import app
from src.risk.calculator import URSCalculator
from src.explainability.explainer import RiskExplainer

client = TestClient(app)

def test_calculator_contributions_sum_equals_urs():
    calc = URSCalculator()
    # Test case 1: Standard inputs
    urs = calc.calculate(
        anomaly_score=0.8,
        reconstruction_error=0.05,
        confidence_score=0.9,
        cpu_usage=85.0,
        memory_usage=70.0,
        network_usage=500000.0,
        historical_frequency=0.2,
        disk_usage=45.0
    )
    
    contribs = calc.get_contributions()
    assert contribs is not None
    assert len(contribs) == 9 # 8 parameters + 1 asset criticality
    
    total_contributions = sum(item["contribution"] for item in contribs.values())
    assert abs(total_contributions - urs) < 1e-5
    
    # Test case 2: Clipped inputs (extremely high values to force clipping to 100.0)
    urs_clipped = calc.calculate(
        anomaly_score=1.0,
        reconstruction_error=1.0,
        confidence_score=1.0,
        cpu_usage=100.0,
        memory_usage=100.0,
        network_usage=100000000.0,
        historical_frequency=1.0,
        disk_usage=100.0
    )
    assert urs_clipped == 100.0
    contribs_clipped = calc.get_contributions()
    total_clipped = sum(item["contribution"] for item in contribs_clipped.values())
    assert abs(total_clipped - 100.0) < 1e-5

def test_top_contributor_selection():
    calc = URSCalculator()
    explainer = RiskExplainer(calc)
    
    # Force CPU to be the highest contributor
    # CPU: weight 0.1, value 95 -> raw contrib 9.5
    # Memory: weight 0.1, value 20 -> raw contrib 2.0
    # Network: value 10 -> raw contrib 1.0
    # Anomaly score: value 10 -> weight 0.3, raw contrib 3.0
    # Reconstruction: value 10 -> weight 0.2, raw contrib 2.0
    # Hist freq: value 10 -> raw contrib 1.0
    # Conf: value 10 -> raw contrib 1.0
    urs = calc.calculate(
        anomaly_score=0.1,
        reconstruction_error=0.1,
        confidence_score=0.1,
        cpu_usage=95.0,
        memory_usage=20.0,
        network_usage=100000.0,
        historical_frequency=0.1,
        disk_usage=10.0
    )
    explanation = explainer.generate_explanation(urs)
    assert explanation["topContributor"] == "CPU"
    
    # Force Anomaly Score to be the highest contributor
    # Anomaly: value 90 -> weight 0.3 -> raw contrib 27.0
    # CPU: value 10 -> raw contrib 1.0
    urs = calc.calculate(
        anomaly_score=0.9,
        reconstruction_error=0.1,
        confidence_score=0.1,
        cpu_usage=10.0,
        memory_usage=10.0,
        network_usage=100000.0,
        historical_frequency=0.1,
        disk_usage=10.0
    )
    explanation = explainer.generate_explanation(urs)
    assert explanation["topContributor"] == "Anomaly Score"

def test_json_schema_validation():
    payload = {
        "anomaly_score": 0.8,
        "reconstruction_error": 0.05,
        "confidence_score": 0.9,
        "cpu_usage": 85.0,
        "memory_usage": 70.0,
        "disk_usage": 40.0,
        "network_usage": 500000.0
    }
    
    res = client.post("/risk/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    # Validate expected keys at top level
    assert "risk_score" in data
    assert "decision" in data
    assert "reason" in data
    assert "contributors" in data
    assert "topContributor" in data
    assert "urs" in data # backward compatibility check
    assert "status" in data # backward compatibility check
    
    # Validate types
    assert isinstance(data["risk_score"], (int, float))
    assert isinstance(data["decision"], str)
    assert isinstance(data["reason"], str)
    assert isinstance(data["contributors"], list)
    assert isinstance(data["topContributor"], str)
    
    # Validate contributors structure
    for contributor in data["contributors"]:
        assert "parameter" in contributor
        assert "value" in contributor
        assert "weight" in contributor
        assert "contribution" in contributor
        assert "reason" in contributor
        
        assert isinstance(contributor["parameter"], str)
        assert isinstance(contributor["value"], (int, float))
        assert isinstance(contributor["weight"], (int, float))
        assert isinstance(contributor["contribution"], (int, float))
        assert isinstance(contributor["reason"], str)
