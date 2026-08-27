import pytest
import sys
import pathlib

engine_root = str(pathlib.Path(__file__).parents[1])
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

from src.timeline_builder import TimelineBuilder
from src.prediction_models import default_context

def test_timeline_builder_empty_context():
    builder = TimelineBuilder(0.0)
    timeline = builder.build()
    
    assert len(timeline) == 5
    for entry in timeline:
        assert entry["projected_urs"] == 0.0
        assert entry["business_impact_level"] == "Informational"
        assert len(entry["events"]) == 0

def test_timeline_builder_high_urs_worsening():
    current_urs = 75.0
    context = default_context()
    context["telemetry_trend"] = "worsening"
    context["critical_count"] = 1
    
    builder = TimelineBuilder(current_urs, context=context)
    timeline = builder.build()
    
    last_entry = timeline[-1]
    assert last_entry["projected_urs"] > current_urs
    assert last_entry["business_impact_level"] in ("High", "Critical")
    
    phases = [evt["attack_phase"] for evt in last_entry["events"]]
    assert "Impact" in phases
    assert "Privilege Escalation" in phases
