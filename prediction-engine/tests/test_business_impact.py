import pytest
import sys
import pathlib

engine_root = str(pathlib.Path(__file__).parents[1])
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

from src.business_impact import calculate_business_impact

def test_calculate_business_impact_no_findings():
    # 10.0 to 10.2 is within 5% growth threshold, so it will be stable
    res = calculate_business_impact(10.0, 10.2)
    assert res["overall"] < 20.0
    assert res["level"] == "Low"
    assert res["trend"] == "stable"
    assert len(res["explanation"]) > 0

def test_calculate_business_impact_with_findings():
    finding_counts = {
        "Critical": 2,
        "High": 1
    }
    res = calculate_business_impact(70.0, 85.0, finding_counts=finding_counts)
    
    assert res["scores"]["compliance"] > 70.0
    assert res["overall"] > 60.0
    assert res["level"] in ("High", "Critical")
    assert res["trend"] == "increasing"
    assert any("Critical" in exp for exp in res["explanation"])
