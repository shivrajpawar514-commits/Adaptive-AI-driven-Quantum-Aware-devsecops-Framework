import pytest
import sys
import pathlib

engine_root = str(pathlib.Path(__file__).parents[1])
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

from src.risk_projection import RiskProjection
from src.prediction_models import default_context

def test_risk_projection_default():
    current_urs = 60.0
    projection = RiskProjection(current_urs)
    assert projection.current_urs == current_urs
    assert projection.ctps > 0
    assert "remediation" in projection.factors
    
    val = projection.project(6)
    assert 0.0 <= val <= 100.0

def test_risk_projection_full():
    current_urs = 40.0
    context = default_context()
    context["telemetry_trend"] = "worsening"
    
    projection = RiskProjection(current_urs, context=context)
    res = projection.full_projection([1, 3, 12])
    
    assert set(res.keys()) == {1, 3, 12}
    assert res[12] > res[3] > res[1] > current_urs
