from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import swarms, workflows, mcp, sandboxes
from .services.broker_core import broker_service
from .models.canonical import MCPToolDefinition

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Unified control plane and dynamic engine broker for multi-agent swarms and workflow automation.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware (permitting Flutter client and Dev consoles)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(swarms.router, prefix=settings.API_PREFIX)
app.include_router(workflows.router, prefix=settings.API_PREFIX)
app.include_router(mcp.router, prefix=settings.API_PREFIX)
app.include_router(sandboxes.router, prefix=settings.API_PREFIX)

@app.on_event("startup")
async def startup_event():
    # Register default built-in MCP tools
    broker_service.register_mcp_tool(
        MCPToolDefinition(
            name="n8n_execute_webhook",
            description="Executes an active n8n automation webhook node",
            parameters={"workflow_id": {"type": "string"}, "payload": {"type": "object"}},
            engine_source="n8n"
        )
    )
    broker_service.register_mcp_tool(
        MCPToolDefinition(
            name="langgraph_evaluate_drift",
            description="Evaluates token drift and state machine consistency across swarm actors",
            parameters={"state": {"type": "object"}},
            engine_source="langgraph"
        )
    )

@app.get("/health", tags=["Health"])
async def health_check():
    engines = await broker_service.get_all_engine_health()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "engines": engines
    }

@app.get("/", tags=["UI"])
@app.get("/dashboard", tags=["UI"])
async def serve_ui():
    import os
    from fastapi.responses import FileResponse
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {
        "message": "Welcome to OmniSwarm Unified Platform API",
        "docs": "/docs",
        "version": settings.VERSION
    }
