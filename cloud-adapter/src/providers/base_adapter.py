from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAdapter(ABC):
    @abstractmethod
    def discover_assets(self) -> List[Dict[str, Any]]:
        """
        Discovers active compute instances / assets in the cloud provider.
        """
        pass

    @abstractmethod
    def get_metrics(self, instance_id: str) -> Dict[str, Any]:
        """
        Queries telemetry metric parameters (CPU, memory, storage, networks) for the asset.
        """
        pass

    @abstractmethod
    def assess_security_posture(self, instance_id: str) -> List[Dict[str, Any]]:
        """
        Scans resource configuration parameters to locate security findings.
        """
        pass
