from fastapi import APIRouter, HTTPException
from ..models.canonical import CanonicalWorkflowTrigger, ExecutionRecord
from ..services.broker_core import broker_service

router = APIRouter(prefix="/workflows", tags=["Workflow Automation"])

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
