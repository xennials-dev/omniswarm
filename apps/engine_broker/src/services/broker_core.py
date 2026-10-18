import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.canonical import (
    CanonicalSwarmRequest,
    CanonicalWorkflowTrigger,
    ExecutionRecord,
    ExecutionStatus,
    EngineCategory,
    MCPToolDefinition
)
from ..config import settings
from .adapters.base import BaseEngineAdapter
from .adapters.langgraph_adapter import LangGraphAdapter
from .adapters.crewai_adapter import CrewAIAdapter
from .adapters.n8n_adapter import N8nAdapter

class DynamicEngineBroker:
    """
    Central orchestration and mediation engine for OmniSwarm.
    Dispatches tasks to sidecars and standardizes cross-platform agent/workflow execution.
    """

    def __init__(self):
        self._adapters: Dict[str, BaseEngineAdapter] = {}
        self._executions: Dict[str, ExecutionRecord] = {}
        self._mcp_tools: Dict[str, MCPToolDefinition] = {}
        self._init_adapters()

    def _init_adapters(self):
        # Register Tier-1 Agent adapters
        self.register_adapter(LangGraphAdapter(settings.LANGGRAPH_SIDECAR_URL))
        self.register_adapter(CrewAIAdapter(settings.CREWAI_SIDECAR_URL))

        # Register Tier-1 Workflow adapters
        self.register_adapter(N8nAdapter(settings.N8N_SIDECAR_URL))

    def register_adapter(self, adapter: BaseEngineAdapter):
        self._adapters[adapter.engine_name] = adapter

    def get_adapter(self, engine_name: str) -> Optional[BaseEngineAdapter]:
        return self._adapters.get(engine_name)

    async def get_all_engine_health(self) -> Dict[str, Dict[str, Any]]:
        health_status = {}
        for name, adapter in self._adapters.items():
            is_healthy = await adapter.health_check()
            health_status[name] = {
                "healthy": is_healthy,
                "sidecar_url": adapter.sidecar_url
            }
        return health_status

    async def dispatch_swarm(self, request: CanonicalSwarmRequest) -> ExecutionRecord:
        engine_name = request.engine.value
        adapter = self.get_adapter(engine_name)

        execution = ExecutionRecord(
            target_engine=engine_name,
            category=EngineCategory.AGENT_SWARM,
            status=ExecutionStatus.PENDING,
            input_payload=request.dict()
        )
        self._executions[execution.execution_id] = execution

        if not adapter:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = f"Engine '{engine_name}' is not registered or supported in this deployment."
            return execution

        # Dispatch to engine adapter
        return await adapter.dispatch(execution, request.dict())

    async def dispatch_workflow(self, trigger: CanonicalWorkflowTrigger) -> ExecutionRecord:
        engine_name = trigger.engine.value
        adapter = self.get_adapter(engine_name)

        execution = ExecutionRecord(
            target_engine=engine_name,
            category=EngineCategory.WORKFLOW,
            status=ExecutionStatus.PENDING,
            input_payload=trigger.dict()
        )
        self._executions[execution.execution_id] = execution

        if not adapter:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = f"Workflow engine '{engine_name}' is not registered or supported."
            return execution

        return await adapter.dispatch(execution, trigger.dict())

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        return self._executions.get(execution_id)

    def list_executions(self, limit: int = 50) -> List[ExecutionRecord]:
        return list(self._executions.values())[-limit:]

    # MCP Router Methods
    def register_mcp_tool(self, tool: MCPToolDefinition):
        self._mcp_tools[tool.name] = tool

    def list_mcp_tools(self) -> List[MCPToolDefinition]:
        return list(self._mcp_tools.values())

broker_service = DynamicEngineBroker()
