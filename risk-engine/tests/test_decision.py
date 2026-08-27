from src.decision.engine import DecisionEngine

def test_decision_logic():
    engine = DecisionEngine()
    
    dec, reason = engine.evaluate(15.0, {}, 0.01)
    assert dec == "Normal"
    
    dec, reason = engine.evaluate(45.0, {}, 0.02)
    assert dec == "Monitor"
    
    dec, reason = engine.evaluate(75.0, {}, 0.05)
    assert dec == "Alert"
    
    dec, reason = engine.evaluate(85.0, {}, 0.12)
    assert dec == "High Risk"
    
    dec, reason = engine.evaluate(95.0, {}, 0.25)
    assert dec == "Critical"
