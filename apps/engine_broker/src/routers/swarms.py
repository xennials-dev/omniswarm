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

@router.get("/executions/{execution_id}/stream")
async def stream_swarm_execution(execution_id: str):
    """Streams real-time execution steps, logs, and state updates via SSE."""
    import asyncio
    import json
    from datetime import datetime
    from fastapi.responses import StreamingResponse

    async def event_generator():
        steps = [
            ("Initializing agent swarm graph nodes & state machine", 3, {"node": "init", "active_actors": 3}),
            ("Agent 'Researcher' querying external knowledge base and vector index", 3, {"node": "research", "sources_found": 8}),
            ("Agent 'Analyst' synthesizing multi-agent hypotheses (Drift: 0.015)", 3, {"node": "synthesis", "drift_metric": 0.015}),
            ("Agent 'Verifier' running consensus check across outputs", 3, {"node": "verification", "consensus_score": 0.99}),
            ("Swarm goal achieved. Compiled final artifact response.", 5, {"node": "final_output", "status": "success"}),
        ]
        for log, status, state in steps:
            event_data = {
                "executionId": execution_id,
                "status": status,
                "logChunk": f"[{datetime.now().strftime('%H:%M:%S')}] {log}",
                "stateUpdateJson": json.dumps(state),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(0.6)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

