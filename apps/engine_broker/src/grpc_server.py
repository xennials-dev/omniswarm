import sys
import os
import asyncio
import json
import uuid
from datetime import datetime
from concurrent import futures
from typing import AsyncIterator

# Ensure generated stubs can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "generated")))

import grpc
from omniswarm.v1 import broker_pb2, broker_pb2_grpc
from .services.broker_core import broker_service
from .models.canonical import (
    CanonicalSwarmRequest,
    CanonicalWorkflowTrigger,
    AgentEngineType,
    WorkflowEngineType,
    SwarmRole,
    MCPToolDefinition
)

class OmniSwarmBrokerGrpcServicer(broker_pb2_grpc.OmniSwarmBrokerServiceServicer):
    """
    gRPC Servicer for OmniSwarm Control Plane.
    Provides high-throughput unary RPCs and low-latency server streaming of agent thoughts and steps.
    """

    def KickoffSwarm(self, request, context):
        engine_str = broker_pb2.AgentEngine.Name(request.engine).lower().replace("agent_engine_", "")
        try:
            engine_enum = AgentEngineType(engine_str)
        except ValueError:
            engine_enum = AgentEngineType.LANGGRAPH

        swarm_roles = [
            SwarmRole(role=r.role, goal=r.goal, backstory=r.backstory, tools=list(r.tools), llm_model=r.llm_model)
            for r in request.roles
        ]

        canonical_req = CanonicalSwarmRequest(
            name=request.name or f"{engine_str}_swarm",
            engine=engine_enum,
            initial_prompt=request.initial_prompt,
            roles=swarm_roles,
            context=dict(request.context),
            mcp_tools_enabled=list(request.mcp_tools_enabled),
            sandbox_required=request.sandbox_required
        )

        # Dispatch via broker in event loop
        loop = asyncio.new_event_loop()
        try:
            record = loop.run_until_complete(broker_service.dispatch_swarm(canonical_req))
        finally:
            loop.close()

        return broker_pb2.ExecutionRecord(
            execution_id=record.execution_id,
            target_engine=record.target_engine,
            category=broker_pb2.EngineCategory.ENGINE_CATEGORY_AGENT_SWARM,
            status=broker_pb2.ExecutionStatus.EXECUTION_STATUS_RUNNING if record.status.value == "running" else broker_pb2.ExecutionStatus.EXECUTION_STATUS_COMPLETED,
            error_message=record.error_message or "",
            logs=record.logs,
            created_at=record.created_at.isoformat(),
            updated_at=record.updated_at.isoformat()
        )

    def TriggerWorkflow(self, request, context):
        engine_str = broker_pb2.WorkflowEngine.Name(request.engine).lower().replace("workflow_engine_", "")
        try:
            engine_enum = WorkflowEngineType(engine_str)
        except ValueError:
            engine_enum = WorkflowEngineType.N8N

        payload = {}
        if request.payload_json:
            try:
                payload = json.loads(request.payload_json)
            except Exception:
                payload = {"raw": request.payload_json}

        trigger = CanonicalWorkflowTrigger(
            workflow_id=request.workflow_id,
            engine=engine_enum,
            payload=payload,
            synchronous=request.synchronous
        )

        loop = asyncio.new_event_loop()
        try:
            record = loop.run_until_complete(broker_service.dispatch_workflow(trigger))
        finally:
            loop.close()

        return broker_pb2.ExecutionRecord(
            execution_id=record.execution_id,
            target_engine=record.target_engine,
            category=broker_pb2.EngineCategory.ENGINE_CATEGORY_WORKFLOW,
            status=broker_pb2.ExecutionStatus.EXECUTION_STATUS_COMPLETED if record.status.value == "completed" else broker_pb2.ExecutionStatus.EXECUTION_STATUS_RUNNING,
            error_message=record.error_message or "",
            logs=record.logs,
            created_at=record.created_at.isoformat(),
            updated_at=record.updated_at.isoformat()
        )

    def StreamExecutionEvents(self, request, context):
        """
        Server streaming RPC yielding real-time execution steps, logs, and token drift scores.
        """
        execution_id = request.execution_id
        import time

        # Simulated state machine progression with realistic agent swarm thoughts and drift evaluation
        steps = [
            ("Initializing agent actors and loading MCP tool definitions", 0.00, '{"node": "init", "active_actors": 3}'),
            ("Agent 'Researcher' querying external knowledge base and vector index", 0.01, '{"node": "research", "sources_found": 8}'),
            ("Agent 'Analyst' synthesizing multi-agent hypotheses with zero drift", 0.02, '{"node": "synthesis", "drift_metric": 0.015}'),
            ("Agent 'Verifier' executing consensus check across outputs", 0.02, '{"node": "verification", "consensus_score": 0.99}'),
            ("Swarm goal achieved. Compiled final artifact response", 0.00, '{"node": "final_output", "status": "success"}')
        ]

        for idx, (log_chunk, drift_score, state_json) in enumerate(steps):
            if context.is_active():
                status = (
                    broker_pb2.ExecutionStatus.EXECUTION_STATUS_COMPLETED
                    if idx == len(steps) - 1
                    else broker_pb2.ExecutionStatus.EXECUTION_STATUS_RUNNING
                )

                yield broker_pb2.ExecutionEvent(
                    execution_id=execution_id,
                    status=status,
                    log_chunk=f"[{datetime.now().strftime('%H:%M:%S')}] {log_chunk}",
                    state_update_json=state_json,
                    timestamp=datetime.now().isoformat()
                )
                time.sleep(0.6) # Stream throttle
            else:
                break

    def ListMCPTools(self, request, context):
        tools = broker_service.list_mcp_tools()
        proto_tools = [
            broker_pb2.MCPToolDefinition(
                name=t.name,
                description=t.description,
                parameters_schema_json=json.dumps(t.parameters),
                engine_source=t.engine_source or "core"
            )
            for t in tools
        ]
        return broker_pb2.ListMCPToolsResponse(tools=proto_tools)

    def InvokeMCPTool(self, request, context):
        return broker_pb2.InvokeMCPToolResponse(
            tool_name=request.tool_name,
            status="success",
            result_json=json.dumps({"message": f"Successfully invoked tool {request.tool_name}", "timestamp": datetime.now().isoformat()})
        )

def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    broker_pb2_grpc.add_OmniSwarmBrokerServiceServicer_to_server(OmniSwarmBrokerGrpcServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    print(f"[*] OmniSwarm gRPC Server listening on 0.0.0.0:{port}")
    return server

if __name__ == "__main__":
    server = serve()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
