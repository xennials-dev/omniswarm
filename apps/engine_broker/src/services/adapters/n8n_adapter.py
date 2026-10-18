import httpx
import uuid
import json
import subprocess
from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import BaseEngineAdapter
from ...models.canonical import ExecutionRecord, ExecutionStatus
from ..n8n_template_service import n8n_template_service
from ..workflow_builder_service import workflow_builder_service

class N8nAdapter(BaseEngineAdapter):
    def __init__(self, sidecar_url: str):
        super().__init__(sidecar_url)
        self._deployed_workflows: Dict[str, Dict[str, Any]] = {}
        self._load_seed_templates()

    def _load_seed_templates(self):
        """Pre-seeds the catalog templates into deployed cache on startup."""
        for t in n8n_template_service.list_templates():
            full = n8n_template_service.get_template(t["id"])
            if full:
                wf = full.get("workflow", {})
                self._deployed_workflows[t["id"]] = {
                    "id": t["id"],
                    "name": full.get("name", t.get("name")),
                    "description": full.get("description", ""),
                    "category": full.get("category", "General"),
                    "trigger_type": full.get("trigger_type", "Webhook"),
                    "nodes_count": len(wf.get("nodes", [])),
                    "active": True,
                    "deployed_at": datetime.utcnow().isoformat(),
                    "webhook_url": f"{self.sidecar_url}/webhook/{self._extract_webhook_path(wf)}",
                    "workflow": wf
                }

    def _extract_webhook_path(self, wf: Dict[str, Any]) -> str:
        for node in wf.get("nodes", []):
            if node.get("type") == "n8n-nodes-base.webhook":
                return node.get("parameters", {}).get("path", "omniswarm-hook")
        return "omniswarm-hook"

    @property
    def engine_name(self) -> str:
        return "n8n"

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                res = await client.get(f"{self.sidecar_url}/healthz")
                return res.status_code == 200
        except Exception:
            return False

    async def dispatch(self, execution: ExecutionRecord, payload: Dict[str, Any]) -> ExecutionRecord:
        execution.status = ExecutionStatus.RUNNING
        execution.updated_at = datetime.utcnow()
        workflow_id = payload.get("workflow_id", "")
        
        # Resolve webhook URL
        webhook_path = payload.get("webhook_path")
        if not webhook_path and workflow_id in self._deployed_workflows:
            wf = self._deployed_workflows[workflow_id]["workflow"]
            webhook_path = self._extract_webhook_path(wf)
        if not webhook_path:
            webhook_path = workflow_id

        target_url = f"{self.sidecar_url}/webhook/{webhook_path}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    target_url,
                    json={
                        "execution_id": execution.execution_id,
                        "data": payload.get("payload", {})
                    }
                )
                if res.status_code in (200, 201):
                    execution.status = ExecutionStatus.COMPLETED
                    execution.output_result = res.json() if res.headers.get("content-type") == "application/json" else {"response": res.text}
                    execution.logs.append(f"n8n workflow '{workflow_id}' triggered successfully at {target_url}.")
                else:
                    execution.status = ExecutionStatus.FAILED
                    execution.error_message = f"n8n webhook error ({res.status_code}): {res.text}"
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = f"Failed to trigger n8n at {target_url}: {str(e)}"
            execution.logs.append(execution.error_message)

        return execution

    def list_templates(self, category: Optional[str] = None, query: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return n8n_template_service.list_templates(category=category, query=query, limit=limit)

    def list_categories(self) -> List[str]:
        return n8n_template_service.list_categories()

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        return n8n_template_service.get_template(template_id)

    async def deploy_template(self, template_id: str, custom_params: Dict[str, Any]) -> Dict[str, Any]:
        instantiated = n8n_template_service.instantiate_template(template_id, custom_params)
        if not instantiated:
            raise ValueError(f"Template '{template_id}' not found.")
        
        wf = instantiated["workflow"]
        wf_id = f"tpl_{template_id}_{str(uuid.uuid4())[:6]}"
        return await self.deploy_workflow(wf, workflow_id=wf_id, category=custom_params.get("category", "Template"))

    async def generate_and_deploy_from_prompt(self, prompt: str, name: Optional[str] = None) -> Dict[str, Any]:
        synthesized = workflow_builder_service.generate_workflow_from_prompt(prompt, name)
        wf = synthesized["workflow"]
        return await self.deploy_workflow(wf, workflow_id=synthesized["workflow_id"], category="AI Synthesized")

    async def deploy_workflow(self, workflow_dict: Dict[str, Any], workflow_id: Optional[str] = None, category: str = "Custom") -> Dict[str, Any]:
        valid, msg = workflow_builder_service.validate_workflow(workflow_dict)
        if not valid:
            raise ValueError(f"Invalid workflow graph: {msg}")

        wf_id = workflow_id or str(uuid.uuid4())[:8]
        wf_name = workflow_dict.get("name", f"Workflow {wf_id}")
        webhook_path = self._extract_webhook_path(workflow_dict)

        # Import workflow into n8n container via CLI if docker is accessible
        try:
            workflow_json_str = json.dumps(workflow_dict)
            import_cmd = (
                f"docker exec -i omniswarm-n8n sh -c 'cat > /tmp/{wf_id}.json && "
                f"n8n import:workflow --input=/tmp/{wf_id}.json --activeState=fromJson && "
                f"rm -f /tmp/{wf_id}.json'"
            )
            subprocess.run(import_cmd, shell=True, input=workflow_json_str, text=True, capture_output=True, timeout=10)
        except Exception as e:
            print(f"[N8nAdapter] Container import fallback: {e}")

        record = {
            "id": wf_id,
            "name": wf_name,
            "description": f"OmniSwarm managed workflow: {wf_name}",
            "category": category,
            "trigger_type": "Webhook" if "webhook" in webhook_path else "Schedule",
            "nodes_count": len(workflow_dict.get("nodes", [])),
            "active": True,
            "deployed_at": datetime.utcnow().isoformat(),
            "webhook_url": f"{self.sidecar_url}/webhook/{webhook_path}",
            "workflow": workflow_dict
        }
        self._deployed_workflows[wf_id] = record
        return record

    def list_active_workflows(self) -> List[Dict[str, Any]]:
        return list(self._deployed_workflows.values())

    async def get_status(self, execution_id: str) -> ExecutionRecord:
        return ExecutionRecord(
            execution_id=execution_id,
            target_engine=self.engine_name,
            category=ExecutionRecord.__fields__["category"].default,
            status=ExecutionStatus.RUNNING
        )

    async def cancel(self, execution_id: str) -> bool:
        return True
