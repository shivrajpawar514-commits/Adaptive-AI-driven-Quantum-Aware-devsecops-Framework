from fastapi.testclient import TestClient
from src.api.main import app
from src.context.context_engine import ContextEngine
from src.risk.calculator import URSCalculator

client = TestClient(app)

def test_context_detection():
    engine = ContextEngine()
    
    # Test weekday daytime (2026-07-20 is a Monday)
    t, d, p = engine.detect_context("2026-07-20T10:00:00Z")
    assert t == "Morning"
    assert d == "Weekday"
    assert p == "Business Hours"
    
    # Test weekday afternoon
    t, d, p = engine.detect_context("2026-07-20T14:30:00Z")
    assert t == "Afternoon"
    assert d == "Weekday"
    assert p == "Business Hours"
    
    # Test weekday evening
    t, d, p = engine.detect_context("2026-07-20T20:15:00Z")
    assert t == "Evening"
    assert d == "Weekday"
    assert p == "Business Hours"
    
    # Test weekday night
    t, d, p = engine.detect_context("2026-07-20T23:00:00Z")
    assert t == "Night"
    assert d == "Weekday"
    assert p == "Night"
    
    # Test weekend morning (2026-07-19 is a Sunday)
    t, d, p = engine.detect_context("2026-07-19T09:00:00Z")
    assert t == "Morning"
    assert d == "Weekend"
    assert p == "Weekend"

def test_profile_loading():
    engine = ContextEngine()
    
    profile = engine.get_profile("Business Hours")
    assert profile is not None
    assert "weights" in profile
    assert "thresholds" in profile
    assert profile["contextConfidence"] == 0.95
    
    fallback = engine.get_profile("NonExistentProfile")
    assert fallback["contextConfidence"] == 0.80 # Falls back to Standard

def test_weight_switching_and_adaptive_calculation():
    calc = URSCalculator()
    
    # Under Business Hours profile, anomaly_score weight is 0.20, network is 0.35, cpu is 0.15
    # 2026-07-20T10:00:00Z is weekday morning (Business Hours)
    urs_business = calc.calculate(
        anomaly_score=0.8,
        reconstruction_error=0.05,
        confidence_score=0.9,
        cpu_usage=85.0,
        memory_usage=70.0,
        network_usage=500000.0,
        historical_frequency=0.2,
        disk_usage=45.0,
        timestamp="2026-07-20T10:00:00Z"
    )
    meta_business = calc.get_context_metadata()
    assert meta_business["context"]["profile"] == "Business Hours"
    
    weights_business = meta_business["adaptive_weights"]
    assert weights_business["anomaly_score"] == 0.20
    assert weights_business["network_utilization"] == 0.35
    
    # Under Weekend profile, anomaly_score weight is 0.35, network is 0.20
    # 2026-07-19T10:00:00Z is weekend morning
    urs_weekend = calc.calculate(
        anomaly_score=0.8,
        reconstruction_error=0.05,
        confidence_score=0.9,
        cpu_usage=85.0,
        memory_usage=70.0,
        network_usage=500000.0,
        historical_frequency=0.2,
        disk_usage=45.0,
        timestamp="2026-07-19T10:00:00Z"
    )
    meta_weekend = calc.get_context_metadata()
    assert meta_weekend["context"]["profile"] == "Weekend"
    
    weights_weekend = meta_weekend["adaptive_weights"]
    assert weights_weekend["anomaly_score"] == 0.35
    assert weights_weekend["network_utilization"] == 0.20
    
    assert urs_business != urs_weekend # dynamic profile weight switching creates different URS

def test_api_schema_and_comparison_research():
    payload = {
        "anomaly_score": 0.8,
        "reconstruction_error": 0.05,
        "confidence_score": 0.9,
        "cpu_usage": 85.0,
        "memory_usage": 70.0,
        "disk_usage": 40.0,
        "network_usage": 500000.0,
        "timestamp": "2026-07-20T10:00:00Z", # Business Hours Weekday
        "workload_profile": "Production"
    }
    
    res = client.post("/risk/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    # Verify XAI response extended context schema keys
    assert "context" in data
    assert "timePeriod" in data["context"]
    assert "dayType" in data["context"]
    assert "profile" in data["context"]
    assert data["context"]["profile"] == "Business Hours"
    
    assert "adaptiveWeights" in data
    assert data["adaptiveWeights"]["cpu"] == 0.15
    assert data["adaptiveWeights"]["network"] == 0.35
    
    # Verify comparison research mode metadata
    assert "comparison" in data
    comp = data["comparison"]
    assert "staticURS" in comp
    assert "adaptiveURS" in comp
    assert "difference" in comp
    assert "improvement" in comp
    assert isinstance(comp["difference"], float)
    assert comp["difference"] == round(comp["adaptiveURS"] - comp["staticURS"], 2)
    
    # Verify dynamic reason includes adaptive weight applied
    for contributor in data["contributors"]:
        assert "Applied adaptive weight" or "Adaptive Weight" in contributor["reason"]
    
    # Verify metrics
    assert "contextConfidence" in data
    assert data["contextConfidence"] == 0.95
    assert "profileVersion" in data
    assert data["profileVersion"] == "1.0.0"
    assert "adaptationReason" in data
    assert "lateral movement" in data["adaptationReason"].lower()

def test_ac_urs_backward_compatibility():
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
    
    # Must have the backward compatible keys
    assert "status" in data
    assert data["status"] == "success"
    assert "urs" in data
    assert "decision" in data
    assert "reason" in data
    assert "timestamp" in data
