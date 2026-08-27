class DecisionEngine:
    def __init__(self, thresholds=None):
        if thresholds is None:
            self.thresholds = {
                "normal": 30,
                "monitor": 60,
                "alert": 80,
                "high_risk": 90
            }
        else:
            self.thresholds = thresholds

    def evaluate(self, urs: float, telemetry: dict, recon_error: float, thresholds: dict = None) -> tuple:
        active_thresholds = thresholds if thresholds is not None else self.thresholds
        if urs < active_thresholds["normal"]:
            decision = "Normal"
            reason = "System metrics are within baseline parameters and anomaly rates are low."
        elif urs < active_thresholds["monitor"]:
            decision = "Monitor"
            reason = "Mild deviations detected. Increasing telemetry logging resolution."
        elif urs < active_thresholds["alert"]:
            decision = "Alert"
            reason = f"Significant telemetry metrics deviation. CPU: {telemetry.get('cpu_usage')}% or Memory: {telemetry.get('memory_usage')}% exceeds thresholds."
        elif urs < active_thresholds["high_risk"]:
            decision = "High Risk"
            reason = f"High reconstruction loss ({recon_error:.4f}) coupled with system anomalies indicates active operational threats."
        else:
            decision = "Critical"
            reason = "Extreme telemetry anomaly profile detected. Automated isolation recommended."

        return decision, reason
