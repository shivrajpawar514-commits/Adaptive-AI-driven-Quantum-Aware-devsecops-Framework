import pytest
import sys
import pathlib

# Add prediction-engine root directory to sys.path so we can import src as a package
engine_root = str(pathlib.Path(__file__).parents[1])
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

from src.forecast_engine import PredictiveForecastEngine
from src.prediction_models import default_context

def test_forecast_engine_defaults():
    engine = PredictiveForecastEngine()
    assert engine.horizons == [1, 3, 6, 12, 24]

def test_generate_forecast_deterministic():
    engine = PredictiveForecastEngine()
    current_urs = 50.0
    res = engine.generate_forecast("test-res", current_urs)
    
    assert res["ctps"] > 0
    assert res["projected_urs"][1] >= current_urs
    assert res["projected_urs"][24] >= current_urs
    assert res["risk_trend"] == "stable"
    assert "remediation" in res["factors"]
    assert len(res["explanation"]) > 0
    assert res["algorithm"] == "CTPS-v1.0"

def test_generate_forecast_worsening():
    engine = PredictiveForecastEngine()
    current_urs = 50.0
    context = default_context()
    context["telemetry_trend"] = "worsening"
    context["finding_max_severity"] = "Critical"
    context["finding_count"] = 5
    
    res = engine.generate_forecast("test-res", current_urs, context=context)
    assert res["risk_trend"] == "increasing"
    assert res["projected_urs"][24] > current_urs
    assert any("Critical" in explanation for explanation in res["explanation"])

def test_generate_forecast_improving():
    engine = PredictiveForecastEngine()
    current_urs = 50.0
    context = default_context()
    context["telemetry_trend"] = "improving"
    context["remediation_rate"] = 0.9
    
    res = engine.generate_forecast("test-res", current_urs, context=context)
    assert res["risk_trend"] == "decreasing"
    assert res["projected_urs"][24] < current_urs
