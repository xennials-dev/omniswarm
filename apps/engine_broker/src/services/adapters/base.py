from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ...models.canonical import ExecutionRecord, ExecutionStatus

class BaseEngineAdapter(ABC):
    """
    Abstract base class for all sidecar engine adapters in OmniSwarm.
    Each adapter translates canonical requests to upstream engine APIs.
    """

    def __init__(self, sidecar_url: str):
        self.sidecar_url = sidecar_url.rstrip("/")

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Returns the canonical name of the engine."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Checks if the upstream sidecar is healthy and reachable."""
        pass

    @abstractmethod
    async def dispatch(self, execution: ExecutionRecord, payload: Dict[str, Any]) -> ExecutionRecord:
        """Dispatches an execution task to the upstream sidecar."""
        pass

    @abstractmethod
    async def get_status(self, execution_id: str) -> ExecutionRecord:
        """Polls or retrieves current status from the sidecar."""
        pass

    @abstractmethod
    async def cancel(self, execution_id: str) -> bool:
        """Cancels an in-flight execution."""
        pass
