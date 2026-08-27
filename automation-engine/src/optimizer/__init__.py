from .base import BaseOptimizer
from .deterministic_optimizer import DeterministicPlaybookOptimizer

def get_optimizer(optimizer_type: str = "deterministic") -> BaseOptimizer:
    """Strategy pattern factory to return the configured optimizer layer."""
    if optimizer_type.lower() == "deterministic":
        return DeterministicPlaybookOptimizer()
    raise ValueError(f"Unknown optimizer type: {optimizer_type}")
