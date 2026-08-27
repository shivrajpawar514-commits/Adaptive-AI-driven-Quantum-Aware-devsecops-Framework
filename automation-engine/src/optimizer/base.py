from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..playbook_registry import Playbook

class BaseOptimizer(ABC):
    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Return the optimizer metadata parameters."""
        pass

    @abstractmethod
    def optimize(self, playbooks: List[Playbook], findings: List[Dict[str, Any]], current_urs: float) -> Dict[str, Any]:
        """Perform SOAR playbook chain optimization."""
        pass
