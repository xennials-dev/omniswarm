import httpx
from typing import Any, Dict
from datetime import datetime
from .base import BaseEngineAdapter
from ...models.canonical import ExecutionRecord, ExecutionStatus

class N8nAdapter(BaseEngineAdapter):
    @property
    def engine_name(self) -> str:
        return "n8n"

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.sidecar_url}/healthz")
                return res.status_code == 200
        except Exception:
            return False

    async def dispatch(self, execution: ExecutionRecord, payload: Dict[str, Any]) -> ExecutionRecord:
        execution.status = ExecutionStatus.RUNNING
        execution.updated_at = datetime.utcnow()
        workflow_id = payload.get("workflow_id", "")
        webhook_path = f"{self.sidecar_url}/webhook/{workflow_id}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    webhook_path,
                    json={
                        "execution_id": execution.execution_id,
                        "data": payload.get("payload", {})
                    }
                )
                if res.status_code in (200, 201):
                    execution.status = ExecutionStatus.COMPLETED
                    execution.output_result = res.json() if res.headers.get("content-type") == "application/json" else {"response": res.text}
                    execution.logs.append(f"n8n workflow {workflow_id} triggered successfully.")
                else:
                    execution.status = ExecutionStatus.FAILED
                    execution.error_message = f"n8n webhook error ({res.status_code}): {res.text}"
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = f"Failed to trigger n8n at {webhook_path}: {str(e)}"
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
