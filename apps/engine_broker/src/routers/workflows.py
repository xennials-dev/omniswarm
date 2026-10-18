from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from ..models.canonical import CanonicalWorkflowTrigger, ExecutionRecord
from ..services.broker_core import broker_service
from ..services.adapters.n8n_adapter import N8nAdapter

router = APIRouter(prefix="/workflows", tags=["Workflow Automation"])

class TemplateDeployRequest(BaseModel):
    name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}
    webhook_path: Optional[str] = None

class WorkflowGenerateRequest(BaseModel):
    prompt: str
    name: Optional[str] = None
    deploy_immediately: bool = True

class WorkflowDeployRequest(BaseModel):
    workflow: Dict[str, Any]
    name: Optional[str] = None
    category: Optional[str] = "Custom"

def _get_n8n_adapter() -> N8nAdapter:
    adapter = broker_service.get_adapter("n8n")
    if not adapter or not isinstance(adapter, N8nAdapter):
        raise HTTPException(status_code=503, detail="n8n adapter is not active or available")
    return adapter

@router.get("/templates")
async def list_templates() -> List[Dict[str, Any]]:
    """Lists all available pre-built N8N automation templates."""
    n8n = _get_n8n_adapter()
    return n8n.list_templates()

@router.get("/templates/{template_id}")
async def get_template(template_id: str) -> Dict[str, Any]:
    """Retrieves full definition and node structure of a template."""
    n8n = _get_n8n_adapter()
    tpl = n8n.get_template(template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return tpl

@router.post("/templates/{template_id}/deploy")
async def deploy_template(template_id: str, request: TemplateDeployRequest) -> Dict[str, Any]:
    """Deploys a pre-built template into N8N with custom parameter overrides."""
    n8n = _get_n8n_adapter()
    params = request.parameters or {}
    if request.name:
        params["name"] = request.name
    if request.webhook_path:
        params["webhook_path"] = request.webhook_path

    try:
        return await n8n.deploy_template(template_id, params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate")
async def generate_workflow(request: WorkflowGenerateRequest) -> Dict[str, Any]:
    """Uses the AI Workflow Synthesizer to formulate an N8N workflow graph and optionally deploy it."""
    n8n = _get_n8n_adapter()
    try:
        if request.deploy_immediately:
            return await n8n.generate_and_deploy_from_prompt(request.prompt, request.name)
        else:
            from ..services.workflow_builder_service import workflow_builder_service
            return workflow_builder_service.generate_workflow_from_prompt(request.prompt, request.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/deploy")
async def deploy_custom_workflow(request: WorkflowDeployRequest) -> Dict[str, Any]:
    """Validates and deploys an arbitrary N8N workflow JSON graph."""
    n8n = _get_n8n_adapter()
    try:
        return await n8n.deploy_workflow(request.workflow, category=request.category or "Custom")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/active")
async def list_active_workflows() -> List[Dict[str, Any]]:
    """Lists currently deployed active N8N workflows and webhook endpoints."""
    n8n = _get_n8n_adapter()
    return n8n.list_active_workflows()

@router.post("/trigger", response_model=ExecutionRecord)
async def trigger_workflow(trigger: CanonicalWorkflowTrigger):
    """Triggers an automation workflow on the selected sidecar (n8n, Temporal, etc.)."""
    return await broker_service.dispatch_workflow(trigger)

@router.get("/executions/{execution_id}", response_model=ExecutionRecord)
async def get_workflow_execution(execution_id: str):
    record = broker_service.get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Execution record not found")
    return record
