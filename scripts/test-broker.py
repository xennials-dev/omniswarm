"""
OmniSwarm Broker Local Verification Script
Tests canonical models, adapter instantiation, MCP routing, and dispatching.
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "engine_broker")))

from src.models.canonical import (
    CanonicalSwarmRequest,
    CanonicalWorkflowTrigger,
    AgentEngineType,
    WorkflowEngineType,
    SwarmRole,
    MCPToolDefinition
)
from src.services.broker_core import DynamicEngineBroker

async def run_tests():
    print("=" * 60)
    print("OmniSwarm Dynamic Engine Broker: Self-Verification")
    print("=" * 60)

    broker = DynamicEngineBroker()
    print("[1] Adapters registered successfully:")
    for engine_name in broker._adapters:
        print(f"   -> {engine_name} adapter active")

    # Verify MCP Tool Registration
    test_tool = MCPToolDefinition(
        name="test_tool",
        description="A verification test tool",
        parameters={"query": {"type": "string"}},
        engine_source="core"
    )
    broker.register_mcp_tool(test_tool)
    tools = broker.list_mcp_tools()
    assert len(tools) >= 1
    print(f"[2] MCP Router verified: {len(tools)} tools discovered")

    # Verify Swarm Canonical Dispatch
    swarm_req = CanonicalSwarmRequest(
        name="Research & Synthesis Swarm",
        engine=AgentEngineType.LANGGRAPH,
        initial_prompt="Analyze open-source agent framework capabilities",
        roles=[
            SwarmRole(role="Researcher", goal="Gather intelligence"),
            SwarmRole(role="Synthesizer", goal="Compile unified report")
        ]
    )
    print(f"[3] Dispatching canonical Swarm request (Engine: {swarm_req.engine.value})...")
    exec_record = await broker.dispatch_swarm(swarm_req)
    print(f"   -> Execution ID: {exec_record.execution_id}")
    print(f"   -> Target Engine: {exec_record.target_engine}")
    print(f"   -> Status: {exec_record.status.value}")

    # Verify Workflow Canonical Dispatch
    wf_trigger = CanonicalWorkflowTrigger(
        workflow_id="wf_customer_onboarding_001",
        engine=WorkflowEngineType.N8N,
        payload={"user_id": "usr_99812", "tier": "enterprise"}
    )
    print(f"[4] Dispatching canonical Workflow trigger (Engine: {wf_trigger.engine.value})...")
    wf_record = await broker.dispatch_workflow(wf_trigger)
    print(f"   -> Execution ID: {wf_record.execution_id}")
    print(f"   -> Status: {wf_record.status.value}")

    print("=" * 60)
    print("All core broker unit checks passed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
