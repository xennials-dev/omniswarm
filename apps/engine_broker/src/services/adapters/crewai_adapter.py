import httpx
from typing import Any, Dict
from datetime import datetime
from .base import BaseEngineAdapter
from ...models.canonical import ExecutionRecord, ExecutionStatus

class CrewAIAdapter(BaseEngineAdapter):
    @property
    def engine_name(self) -> str:
        return "crewai"

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.sidecar_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    async def dispatch(self, execution: ExecutionRecord, payload: Dict[str, Any]) -> ExecutionRecord:
        execution.status = ExecutionStatus.RUNNING
        execution.updated_at = datetime.utcnow()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    f"{self.sidecar_url}/crew/kickoff",
                    json={
                        "execution_id": execution.execution_id,
                        "agents": payload.get("roles", []),
                        "tasks": [{"description": payload.get("initial_prompt", "")}],
                        "inputs": payload.get("context", {})
                    }
                )
                if res.status_code in (200, 201, 202):
                    data = res.json()
                    execution.status = ExecutionStatus.COMPLETED
                    execution.output_result = data
                    execution.logs.append(f"CrewAI crew executed successfully.")
                else:
                    execution.status = ExecutionStatus.FAILED
                    execution.error_message = f"CrewAI sidecar error ({res.status_code}): {res.text}"
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = f"Failed to connect to CrewAI sidecar at {self.sidecar_url}: {str(e)}"
            execution.logs.append(execution.error_message)

        return execution

    async def get_status(self, execution_id: str) -> ExecutionRecord:
        return ExecutionRecord(
            execution_id=execution_id,
            target_engine=self.engine_name,
            category=ExecutionRecord.__fields__["category"].default,
            status=ExecutionStatus.RUNNING
        )

    async def cancel(self, execution_id: str) -> bool:
        return True
