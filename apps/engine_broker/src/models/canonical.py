from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class EngineCategory(str, Enum):
    AGENT_SWARM = "agent_swarm"
    WORKFLOW = "workflow"

class AgentEngineType(str, Enum):
    LANGGRAPH = "langgraph"
    CREWAI = "crewai"
    AUTOGEN = "autogen"
    DIFY = "dify"
    METAGPT = "metagpt"
    CHATDEV = "chatdev"
    AGNO = "agno"
    PYDANTIC_AI = "pydantic_ai"
    SMOLAGENTS = "smolagents"
    MASTRA = "mastra"

class WorkflowEngineType(str, Enum):
    N8N = "n8n"
    ACTIVEPIECES = "activepieces"
    WINDMILL = "windmill"
    KESTRA = "kestra"
    AIRFLOW = "airflow"
    TEMPORAL = "temporal"
    CAMUNDA = "camunda"
    NODE_RED = "node_red"
    ARGO = "argo"
    TRIGGER_DEV = "trigger_dev"

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MCPToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    server_id: Optional[str] = None
    engine_source: Optional[str] = None

class SwarmRole(BaseModel):
    role: str
    goal: str
    backstory: Optional[str] = None
    tools: List[str] = Field(default_factory=list)
    llm_model: Optional[str] = "gpt-4o"

class CanonicalSwarmRequest(BaseModel):
    name: str
    engine: AgentEngineType = AgentEngineType.LANGGRAPH
    description: Optional[str] = None
    roles: List[SwarmRole] = Field(default_factory=list)
    initial_prompt: str
    context: Dict[str, Any] = Field(default_factory=dict)
    mcp_tools_enabled: List[str] = Field(default_factory=list)
    sandbox_required: bool = False

class CanonicalWorkflowTrigger(BaseModel):
    workflow_id: str
    engine: WorkflowEngineType = WorkflowEngineType.N8N
    payload: Dict[str, Any] = Field(default_factory=dict)
    synchronous: bool = False

class ExecutionRecord(BaseModel):
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_engine: str
    category: EngineCategory
    status: ExecutionStatus = ExecutionStatus.PENDING
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    output_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SandboxSpec(BaseModel):
    sandbox_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: str = "e2b" # e2b, daytona, gvisor
    template: str = "python-data"
    timeout_seconds: int = 300
    env_vars: Dict[str, str] = Field(default_factory=dict)
