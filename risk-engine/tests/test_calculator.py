from src.risk.calculator import URSCalculator

def test_calculator_range_and_output():
    calc = URSCalculator()
    urs = calc.calculate(
        anomaly_score=0.8,
        reconstruction_error=0.05,
        confidence_score=0.9,
        cpu_usage=85.0,
        memory_usage=70.0,
        network_usage=500000.0,
        historical_frequency=0.2
    )
    assert 0.0 <= urs <= 100.0
