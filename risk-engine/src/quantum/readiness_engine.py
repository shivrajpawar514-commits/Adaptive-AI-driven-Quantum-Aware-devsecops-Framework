import json
import os
from typing import Dict, Any, List

class QuantumReadinessEngine:
    def __init__(self, profiles_path: str = None):
        if profiles_path is None:
            profiles_path = os.path.join(os.path.dirname(__file__), 'quantum_profiles.json')
            
        self.profiles_path = profiles_path
        self.profiles_data = self._load_profiles()

    def _load_profiles(self) -> Dict[str, Any]:
        if os.path.exists(self.profiles_path):
            with open(self.profiles_path, 'r') as f:
                return json.load(f)
        return {"algorithms": {}}

    def evaluate_posture(self, algorithms: List[str] = None) -> Dict[str, Any]:
        """
        Evaluates cryptographic posture and returns quantum readiness metrics and XAI explanations.
        """
        if not algorithms:
            # Default legacy baseline representation
            algorithms = ["RSA-2048", "ECC P-256"]

        profiles = self.profiles_data.get("algorithms", {})
        crypto_details = []
        weights = []
        
        risk_map = {"Very High": 3, "High": 2, "Medium": 1, "Low": 0}
        priority_map = {"Immediate": 2, "Planned": 1, "Completed": 0}
        
        highest_risk_val = -1
        highest_risk_algo = "N/A"
        highest_priority_val = -1
        
        top_recommendation = "No actions required."
        
        for item in algorithms:
            if isinstance(item, dict):
                algo = item.get("algorithm") or item.get("name") or "Unknown"
            else:
                algo = str(item)
                
            # Lookup profile, default to Unknown if not found
            if algo in profiles:
                data = profiles[algo]
            else:
                data = profiles.get("Unknown", {
                    "quantumRisk": "High",
                    "migrationPriority": "Immediate",
                    "readinessWeight": 10,
                    "recommendation": "Audit asset to identify cryptosystem.",
                    "reason": "Unrecognized cryptography posture indicates unverified quantum risk."
                })
                
            risk_str = data["quantumRisk"]
            priority_str = data["migrationPriority"]
            weight = data["readinessWeight"]
            rec = data["recommendation"]
            reason = data["reason"]
            
            weights.append(weight)
            
            # Record details
            crypto_details.append({
                "algorithm": algo,
                "quantumRisk": risk_str,
                "readinessWeight": weight,
                "recommendation": rec,
                "reason": reason
            })
            
            # Map values for aggregations
            risk_val = risk_map.get(risk_str, 0)
            priority_val = priority_map.get(priority_str, 0)
            
            # Determine highest risk and associated properties
            # If multiple algorithms have same risk, prioritize picking the one with lower readiness weight (weaker link)
            if risk_val > highest_risk_val or (risk_val == highest_risk_val and weight < profiles.get(highest_risk_algo, {}).get("readinessWeight", 100)):
                highest_risk_val = risk_val
                highest_risk_algo = algo
                top_recommendation = rec
                
            if priority_val > highest_priority_val:
                highest_priority_val = priority_val

        # Reverse maps to get string representations
        risk_rev = {3: "Very High", 2: "High", 1: "Medium", 0: "Low"}
        priority_rev = {2: "Immediate", 1: "Planned", 0: "Completed"}
        
        overall_risk = risk_rev.get(max(0, highest_risk_val), "Low")
        overall_priority = priority_rev.get(max(0, highest_priority_val), "Completed")
        
        # Calculate score (average of algorithm weights)
        if weights:
            score = int(round(sum(weights) / len(weights)))
        else:
            score = 100
            
        # Determine classification
        if score <= 25:
            classification = "Poor"
        elif score <= 50:
            classification = "Moderate"
        elif score <= 75:
            classification = "Good"
        else:
            classification = "Excellent"

        # Construct dynamic human-readable explanation summary
        if overall_risk in ("Very High", "High"):
            summary_explanation = (
                f"Monitored assets have an overall quantum readiness classification of {classification} "
                f"with a score of {score}/100. The presence of legacy algorithms like {highest_risk_algo} "
                f"presents a {overall_risk} quantum risk, requiring {overall_priority.lower()} migration "
                f"planning to post-quantum alternatives."
            )
        elif overall_risk == "Medium":
            summary_explanation = (
                f"Monitored assets show moderate preparedness with a score of {score}/100 "
                f"(classification: {classification}). Security postures require planned updates for "
                f"elliptic curve cryptography or related standards."
            )
        else:
            summary_explanation = (
                f"Monitored assets have achieved an Excellent quantum readiness rating of {score}/100. "
                "Cryptographic systems are fully post-quantum secure with verified ML-KEM or hybrid implementations."
            )

        return {
            "quantumReadiness": {
                "score": score,
                "classification": classification,
                "migrationPriority": overall_priority,
                "overallQuantumRisk": overall_risk
            },
            "cryptography": crypto_details,
            "quantumExplanation": summary_explanation,
            "dashboardData": {
                "migrationPriority": overall_priority,
                "topRecommendation": top_recommendation,
                "highestQuantumRiskAlgorithm": highest_risk_algo,
                "overallQuantumReadiness": classification,
                "Migration Priority": overall_priority,
                "Top Recommendation": top_recommendation,
                "Highest Quantum Risk Algorithm": highest_risk_algo,
                "Overall Quantum Readiness": classification
            }
        }
