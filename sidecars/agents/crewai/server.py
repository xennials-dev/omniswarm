import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn

app = FastAPI(title="OmniSwarm CrewAI Sidecar", version="0.1.0")

class KickoffRequest(BaseModel):
    execution_id: str
    agents: List[Dict[str, Any]] = []
    tasks: List[Dict[str, Any]] = []
    inputs: Dict[str, Any] = {}

@app.get("/health")
async def health():
    return {"status": "ok", "sidecar": "crewai"}

@app.post("/crew/kickoff")
async def kickoff(req: KickoffRequest):
    return {
        "execution_id": req.execution_id,
        "status": "completed",
        "result": {
            "crew_output": f"Crew completed tasks: {[t.get('description', '') for t in req.tasks]}",
            "collaborating_agents": len(req.agents)
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8200))
    uvicorn.run(app, host="0.0.0.0", port=port)
