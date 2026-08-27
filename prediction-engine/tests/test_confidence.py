import pytest
import sys
import pathlib

engine_root = str(pathlib.Path(__file__).parents[1])
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

from src.confidence import calculate_confidence

def test_calculate_confidence_high():
    metrics = {
        "telemetry": 90.0,
        "stability": 90.0,
        "criticality": 90.0,
        "historical": 90.0
    }
    res = calculate_confidence(metrics)
    assert res["score"] == 90.0
    assert res["level"] == "High"
    assert len(res["explanation"]) > 0

def test_calculate_confidence_low():
    metrics = {
        "telemetry": 20.0,
        "stability": 20.0,
        "criticality": 20.0,
        "historical": 20.0
    }
    res = calculate_confidence(metrics)
    assert res["score"] == 20.0
    assert res["level"] == "Low"

def test_calculate_confidence_freshness_discount():
    metrics = {
        "telemetry": 100.0,
        "stability": 100.0,
        "criticality": 100.0,
        "historical": 100.0
    }
    res = calculate_confidence(metrics, freshness=50.0)
    assert res["score"] == 50.0
    assert res["level"] == "Medium"
    assert any("freshness" in exp for exp in res["explanation"])

def test_calculate_confidence_missing_keys():
    metrics = {
        "telemetry": 100.0
    }
    with pytest.raises(ValueError):
        calculate_confidence(metrics)
