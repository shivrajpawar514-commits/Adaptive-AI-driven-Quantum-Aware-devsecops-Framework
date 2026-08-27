import os

CLOUD_ADAPTER_URL = os.getenv("CLOUD_ADAPTER_URL", "http://localhost:7000")
RISK_ENGINE_URL = os.getenv("RISK_ENGINE_URL", "http://localhost:8500")
DIGITAL_TWIN_URL = os.getenv("DIGITAL_TWIN_URL", "http://localhost:9500")
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://localhost:8000")

# Constants and configurations for Playbook Optimization Layer
SCORING_WEIGHTS = {
    "severity": 2.0,
    "urs": 0.3,
    "recovery": 2.5,
    "policy_priority": 2.0,
    "confidence": 5.0,
    "disruption": -1.5,
    "execution_time": -0.1
}

SEVERITY_WEIGHTS = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1
}

POLICY_PRIORITY_WEIGHTS = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1
}
