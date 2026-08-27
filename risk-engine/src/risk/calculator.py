import json
import os
import threading
from src.context.context_engine import ContextEngine

class URSCalculator:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'weights.json')
            
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "weights": {
                    "anomaly_score": 0.3,
                    "reconstruction_error": 0.2,
                    "cpu_utilization": 0.1,
                    "memory_utilization": 0.1,
                    "network_utilization": 0.1,
                    "historical_anomaly_frequency": 0.1,
                    "confidence_score": 0.1,
                    "disk_utilization": 0.0
                },
                "asset_criticality": 1.0,
                "thresholds": {
                    "normal": 30,
                    "monitor": 60,
                    "alert": 80,
                    "high_risk": 90
                }
            }

        # Ensure disk_utilization is present in weights
        if "disk_utilization" not in self.config["weights"]:
            self.config["weights"]["disk_utilization"] = 0.0

        self.context_engine = ContextEngine()
        self._thread_local = threading.local()

    def calculate(self, anomaly_score: float, reconstruction_error: float, confidence_score: float,
                  cpu_usage: float, memory_usage: float, network_usage: float,
                  historical_frequency: float, disk_usage: float = 0.0,
                  timestamp: str = None, workload_profile: str = "Development") -> float:
        crit = self.config["asset_criticality"]

        recon_norm = min(reconstruction_error * 100, 100.0)
        net_norm = min(network_usage / 1000000.0, 100.0)

        # Raw values matching parameter weights
        val_anomaly_score = anomaly_score * 100
        val_reconstruction_error = recon_norm
        val_cpu_utilization = cpu_usage
        val_memory_utilization = memory_usage
        val_network_utilization = net_norm
        val_historical_anomaly_frequency = historical_frequency * 100
        val_confidence_score = confidence_score * 100
        val_disk_utilization = disk_usage

        # 1. Compute Static URS (using static weights from config)
        w_static = self.config["weights"]
        static_raw = (
            w_static.get("anomaly_score", 0.3) * val_anomaly_score +
            w_static.get("reconstruction_error", 0.2) * val_reconstruction_error +
            w_static.get("cpu_utilization", 0.1) * val_cpu_utilization +
            w_static.get("memory_utilization", 0.1) * val_memory_utilization +
            w_static.get("network_utilization", 0.1) * val_network_utilization +
            w_static.get("historical_anomaly_frequency", 0.1) * val_historical_anomaly_frequency +
            w_static.get("confidence_score", 0.1) * val_confidence_score +
            w_static.get("disk_utilization", 0.0) * val_disk_utilization
        )
        static_urs = max(0.0, min(static_raw * crit, 100.0))

        # 2. Detect Context & Load Adaptive Profile
        time_period, day_type, profile_name = self.context_engine.detect_context(timestamp, workload_profile)
        profile_data = self.context_engine.get_profile(profile_name)
        w_adaptive = profile_data["weights"]
        
        # Save context attributes in thread-local storage for explanations
        self._thread_local.context = {
            "timePeriod": time_period,
            "dayType": day_type,
            "profile": profile_name
        }
        self._thread_local.adaptive_weights = w_adaptive
        self._thread_local.static_urs = static_urs
        self._thread_local.context_confidence = profile_data.get("contextConfidence", 1.0)
        self._thread_local.profile_version = self.context_engine.get_version()
        self._thread_local.adaptation_reason = profile_data.get("adaptationReason", "")
        self._thread_local.adaptive_thresholds = profile_data.get("thresholds", self.config["thresholds"])

        # 3. Compute Adaptive Contributions
        self._thread_local.contributions = {
            "anomaly_score": {
                "value": val_anomaly_score,
                "weight": w_adaptive.get("anomaly_score", 0.0),
                "contribution": w_adaptive.get("anomaly_score", 0.0) * val_anomaly_score
            },
            "reconstruction_error": {
                "value": val_reconstruction_error,
                "weight": w_adaptive.get("reconstruction_error", 0.0),
                "contribution": w_adaptive.get("reconstruction_error", 0.0) * val_reconstruction_error
            },
            "cpu_utilization": {
                "value": val_cpu_utilization,
                "weight": w_adaptive.get("cpu_utilization", 0.0),
                "contribution": w_adaptive.get("cpu_utilization", 0.0) * val_cpu_utilization
            },
            "memory_utilization": {
                "value": val_memory_utilization,
                "weight": w_adaptive.get("memory_utilization", 0.0),
                "contribution": w_adaptive.get("memory_utilization", 0.0) * val_memory_utilization
            },
            "network_utilization": {
                "value": val_network_utilization,
                "weight": w_adaptive.get("network_utilization", 0.0),
                "contribution": w_adaptive.get("network_utilization", 0.0) * val_network_utilization
            },
            "historical_anomaly_frequency": {
                "value": val_historical_anomaly_frequency,
                "weight": w_adaptive.get("historical_anomaly_frequency", 0.0),
                "contribution": w_adaptive.get("historical_anomaly_frequency", 0.0) * val_historical_anomaly_frequency
            },
            "confidence_score": {
                "value": val_confidence_score,
                "weight": w_adaptive.get("confidence_score", 0.0),
                "contribution": w_adaptive.get("confidence_score", 0.0) * val_confidence_score
            },
            "disk_utilization": {
                "value": val_disk_utilization,
                "weight": w_adaptive.get("disk_utilization", 0.0),
                "contribution": w_adaptive.get("disk_utilization", 0.0) * val_disk_utilization
            }
        }

        raw_score = sum(item["contribution"] for item in self._thread_local.contributions.values())

        # Asset Criticality contribution using adaptive raw score
        self._thread_local.contributions["asset_criticality"] = {
            "value": crit,
            "weight": 1.0,
            "contribution": raw_score * (crit - 1.0)
        }

        total_score = raw_score * crit
        urs = max(0.0, min(total_score, 100.0))

        # Proportional adjustment of all contributions for clipping
        if total_score != urs:
            if total_score > 0.0:
                ratio = urs / total_score
                for key in self._thread_local.contributions:
                    self._thread_local.contributions[key]["contribution"] *= ratio
            else:
                for key in self._thread_local.contributions:
                    self._thread_local.contributions[key]["contribution"] = 0.0

        return urs

    def get_contributions(self) -> dict:
        return getattr(self._thread_local, 'contributions', {})

    def get_context_metadata(self) -> dict:
        return {
            "context": getattr(self._thread_local, 'context', {}),
            "adaptive_weights": getattr(self._thread_local, 'adaptive_weights', {}),
            "static_urs": getattr(self._thread_local, 'static_urs', 0.0),
            "context_confidence": getattr(self._thread_local, 'context_confidence', 1.0),
            "profile_version": getattr(self._thread_local, 'profile_version', "1.0.0"),
            "adaptation_reason": getattr(self._thread_local, 'adaptation_reason', ""),
            "adaptive_thresholds": getattr(self._thread_local, 'adaptive_thresholds', self.config["thresholds"])
        }


