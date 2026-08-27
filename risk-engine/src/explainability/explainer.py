from typing import Dict, List, Any

class RiskExplainer:
    def __init__(self, calculator):
        self.calculator = calculator

    def generate_explanation(self, risk_score: float) -> Dict[str, Any]:
        """
        Generates explanation JSON structure containing parameter values, weights,
        contributions, reasons, identifying the top contributor, and context metadata.
        """
        contributions = self.calculator.get_contributions()
        meta = self.calculator.get_context_metadata()
        context_info = meta.get("context", {})
        adaptive_weights = meta.get("adaptive_weights", {})
        
        # Mapping parameter keys from the calculator to JSON representation
        param_mapping = {
            "cpu_utilization": "CPU",
            "memory_utilization": "Memory",
            "disk_utilization": "Disk",
            "network_utilization": "Network",
            "anomaly_score": "Anomaly Score",
            "reconstruction_error": "Reconstruction Error",
            "historical_anomaly_frequency": "Historical Frequency",
            "confidence_score": "Confidence",
            "asset_criticality": "Asset Criticality"
        }

        contributors_list = []
        
        for key, display_name in param_mapping.items():
            if key not in contributions:
                continue
                
            item = contributions[key]
            value = item["value"]
            weight = item["weight"]
            contrib_val = item["contribution"]
            
            # Generate custom reasoning text based on values
            base_reason = self._generate_reason(key, value)
            
            # Append adaptive weight detail to the explanation string
            reason = f"{base_reason} (Adaptive Weight: {round(weight, 4) if isinstance(weight, float) else weight})"
            
            contributors_list.append({
                "parameter": display_name,
                "value": round(value, 2) if isinstance(value, float) else value,
                "weight": round(weight, 4) if isinstance(weight, float) else weight,
                "contribution": round(contrib_val, 2) if isinstance(contrib_val, float) else contrib_val,
                "reason": reason
            })
            
        # Determine top contributor (excluding Asset Criticality as it is a scaling multiplier)
        weighted_contributors = [c for c in contributors_list if c["parameter"] != "Asset Criticality"]
        if weighted_contributors:
            top_contributor = max(weighted_contributors, key=lambda x: x["contribution"])["parameter"]
        else:
            top_contributor = "N/A"

        # Map long keys to short keys for adaptiveWeights JSON output
        key_mapping = {
            "cpu_utilization": "cpu",
            "memory_utilization": "memory",
            "disk_utilization": "disk",
            "network_utilization": "network",
            "anomaly_score": "anomaly",
            "reconstruction_error": "reconstruction",
            "confidence_score": "confidence",
            "historical_anomaly_frequency": "historical"
        }
        
        adaptive_weights_output = {}
        for long_key, short_key in key_mapping.items():
            if long_key in adaptive_weights:
                adaptive_weights_output[short_key] = round(adaptive_weights[long_key], 4)
            
        return {
            "risk_score": round(risk_score, 2),
            "contributors": contributors_list,
            "topContributor": top_contributor,
            "context": {
                "timePeriod": context_info.get("timePeriod", "Standard"),
                "dayType": context_info.get("dayType", "Weekday"),
                "profile": context_info.get("profile", "Standard")
            },
            "adaptiveWeights": adaptive_weights_output
        }

    def _generate_reason(self, key: str, value: float) -> str:
        """
        Generates dynamic explanations for metric states based on baseline values.
        """
        if key == "cpu_utilization":
            if value > 80:
                return "CPU utilization exceeded adaptive threshold."
            elif value > 50:
                return "CPU utilization above expected baseline."
            else:
                return "CPU utilization is within normal limits."
        elif key == "memory_utilization":
            if value > 80:
                return "Memory utilization critically high."
            elif value > 60:
                return "Memory utilization above expected baseline."
            else:
                return "Memory utilization is within normal limits."
        elif key == "disk_utilization":
            if value > 80:
                return "Disk space utilization is critically high."
            elif value > 50:
                return "Disk utilization above expected baseline."
            else:
                return "Disk space utilization is within normal limits."
        elif key == "network_utilization":
            if value > 80:
                return "Network utilization critically high, indicating possible flooding/exfiltration."
            elif value > 40:
                return "Network traffic elevated above normal levels."
            else:
                return "Network traffic is normal."
        elif key == "anomaly_score":
            if value >= 70:
                return "Highly anomalous activity signature detected by AI Engine."
            elif value >= 30:
                return "Moderate system anomaly pattern detected."
            else:
                return "AI Engine anomaly index is within normal bounds."
        elif key == "reconstruction_error":
            if value >= 80:
                return "Severe autoencoder reconstruction error, indicating anomalous operational states."
            elif value >= 30:
                return "Elevated reconstruction error, suggesting moderate deviance."
            else:
                return "System reconstruction error is normal."
        elif key == "historical_anomaly_frequency":
            if value >= 50:
                return "High historical anomaly frequency, indicating chronic instability."
            elif value >= 10:
                return "Elevated baseline of historical anomaly occurrences."
            else:
                return "Low anomaly occurrence history."
        elif key == "confidence_score":
            if value >= 80:
                return "High confidence in anomaly classification accuracy."
            elif value >= 40:
                return "Moderate confidence in classification accuracy."
            else:
                return "Lower confidence rating for classification accuracy."
        elif key == "asset_criticality":
            if value > 1.5:
                return "Asset criticality factor heavily amplifies risk score."
            elif value > 1.0:
                return "Asset criticality factor amplifies risk score."
            else:
                return "Standard baseline asset criticality multiplier."
        return "Metric value is normal."

