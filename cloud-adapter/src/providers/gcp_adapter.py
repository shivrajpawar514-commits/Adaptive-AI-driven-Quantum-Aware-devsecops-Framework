from typing import List, Dict, Any
from .base_adapter import BaseAdapter

class GCPAdapter(BaseAdapter):
    def __init__(self):
        print("GCPAdapter initialized in placeholder mode.")

    def discover_assets(self) -> List[Dict[str, Any]]:
        return []

    def get_metrics(self, instance_id: str) -> Dict[str, Any]:
        return {}

    def assess_security_posture(self, instance_id: str) -> List[Dict[str, Any]]:
        return []
