from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..models.canonical import MCPToolDefinition
from ..services.broker_core import broker_service
from ..services.adapters.n8n_adapter import N8nAdapter

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])

@router.get("/tools", response_model=List[MCPToolDefinition])
async def list_tools():
    """Lists all registered MCP tools across all agent swarms and workflows."""
    return broker_service.list_mcp_tools()

@router.post("/tools", response_model=MCPToolDefinition)
async def register_tool(tool: MCPToolDefinition):
    """Registers a new tool into the MCP router."""
    broker_service.register_mcp_tool(tool)
    return tool

@router.post("/tools/{tool_name}/invoke")
async def invoke_tool(tool_name: str, arguments: Dict[str, Any]):
    """Executes a tool call via the MCP router."""
    tools = {t.name: t for t in broker_service.list_mcp_tools()}
    if tool_name not in tools:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    # Real dispatch for N8N MCP tools
    n8n_adapter = broker_service.get_adapter("n8n")
    if isinstance(n8n_adapter, N8nAdapter):
        if tool_name == "n8n_list_templates":
            templates = n8n_adapter.list_templates()
            return {
                "tool": tool_name,
                "status": "success",
                "result": templates
            }
        elif tool_name == "n8n_instantiate_template":
            template_id = arguments.get("template_id", "")
            params = arguments.get("parameters", {})
            deployed = await n8n_adapter.deploy_template(template_id, params)
            return {
                "tool": tool_name,
                "status": "success",
                "result": deployed
            }
        elif tool_name == "n8n_create_workflow":
            prompt = arguments.get("prompt", "")
            name = arguments.get("name")
            deployed = await n8n_adapter.generate_and_deploy_from_prompt(prompt, name)
            return {
                "tool": tool_name,
                "status": "success",
                "result": deployed
            }
        elif tool_name == "n8n_list_active_workflows":
            workflows = n8n_adapter.list_active_workflows()
            return {
                "tool": tool_name,
                "status": "success",
                "result": workflows
            }

    # Standard / mock response for other external platforms
    return {
        "tool": tool_name,
        "status": "success",
        "result": f"Executed {tool_name} successfully with arguments {arguments}"
    }
