from typing import Dict, Optional
from .execution_manager import ExecutionSession


class ExecutionRepository:
    """Interface for execution session persistence"""
    def save(self, session: ExecutionSession) -> None:
        raise NotImplementedError

    def get(self, execution_id: str) -> Optional[ExecutionSession]:
        raise NotImplementedError

    def list_all(self) -> Dict[str, ExecutionSession]:
        raise NotImplementedError


class InMemoryExecutionRepository(ExecutionRepository):
    def __init__(self):
        self._store: Dict[str, ExecutionSession] = {}

    def save(self, session: ExecutionSession) -> None:
        self._store[session.executionId] = session

    def get(self, execution_id: str) -> Optional[ExecutionSession]:
        return self._store.get(execution_id)

    def list_all(self) -> Dict[str, ExecutionSession]:
        return self._store.copy()
