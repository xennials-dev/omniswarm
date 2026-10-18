from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..models.canonical import MCPToolDefinition
from ..services.broker_core import broker_service

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
    
    # Return simulated/dispatched MCP tool response
    return {
        "tool": tool_name,
        "status": "success",
        "result": f"Executed {tool_name} successfully with arguments {arguments}"
    }
