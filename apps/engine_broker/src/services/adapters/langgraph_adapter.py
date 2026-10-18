import httpx
from typing import Any, Dict
from datetime import datetime
from .base import BaseEngineAdapter
from ...models.canonical import ExecutionRecord, ExecutionStatus

class LangGraphAdapter(BaseEngineAdapter):
    @property
    def engine_name(self) -> str:
        return "langgraph"

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
                    f"{self.sidecar_url}/runs",
                    json={
                        "execution_id": execution.execution_id,
                        "graph_state": payload.get("context", {}),
                        "prompt": payload.get("initial_prompt", ""),
                        "roles": payload.get("roles", [])
                    }
                )
                if res.status_code in (200, 201, 202):
                    data = res.json()
                    execution.status = ExecutionStatus.RUNNING if data.get("async") else ExecutionStatus.COMPLETED
                    execution.output_result = data.get("result", data)
                    execution.logs.append(f"Dispatched to LangGraph sidecar: status {res.status_code}")
                else:
                    execution.status = ExecutionStatus.FAILED
                    execution.error_message = f"LangGraph sidecar error ({res.status_code}): {res.text}"
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = f"Failed to connect to LangGraph sidecar at {self.sidecar_url}: {str(e)}"
            execution.logs.append(execution.error_message)

        return execution

    async def get_status(self, execution_id: str) -> ExecutionRecord:
        # Mock/query sidecar status
        return ExecutionRecord(
            execution_id=execution_id,
            target_engine=self.engine_name,
            category=ExecutionRecord.__fields__["category"].default,
            status=ExecutionStatus.RUNNING
        )

    async def cancel(self, execution_id: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.delete(f"{self.sidecar_url}/runs/{execution_id}")
                return res.status_code in (200, 204)
        except Exception:
            return False
