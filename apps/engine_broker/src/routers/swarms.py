from fastapi import APIRouter, HTTPException
from typing import List
from ..models.canonical import CanonicalSwarmRequest, ExecutionRecord
from ..services.broker_core import broker_service

router = APIRouter(prefix="/swarms", tags=["Swarm Orchestration"])

@router.post("/kickoff", response_model=ExecutionRecord)
async def kickoff_swarm(request: CanonicalSwarmRequest):
    """Dispatches a multi-agent swarm task to the selected engine sidecar."""
    return await broker_service.dispatch_swarm(request)

@router.get("/executions/{execution_id}", response_model=ExecutionRecord)
async def get_swarm_execution(execution_id: str):
    record = broker_service.get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Execution record not found")
    return record

@router.get("/executions", response_model=List[ExecutionRecord])
async def list_swarm_executions():
    return broker_service.list_executions()
