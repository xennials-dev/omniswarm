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
    # Register the complete suite of 20 MCP-compatible platform tools
    all_tools = [
        MCPToolDefinition(
            name="github_repo_manager",
            description="Access repositories, pull code, manage branches, and triage GitHub issues",
            parameters={"repo": {"type": "string"}, "action": {"type": "string"}},
            engine_source="github"
        ),
        MCPToolDefinition(
            name="docker_container_ops",
            description="Inspect, start, stop, and monitor container statuses and images",
            parameters={"container_id": {"type": "string"}, "command": {"type": "string"}},
            engine_source="docker"
        ),
        MCPToolDefinition(
            name="kubernetes_cluster_ops",
            description="Manage cluster deployments, pods, services, and Helm releases",
            parameters={"namespace": {"type": "string"}, "resource": {"type": "string"}},
            engine_source="kubernetes"
        ),
        MCPToolDefinition(
            name="terraform_iac_manager",
            description="Execute plan, apply, and state tracking for infrastructure-as-code",
            parameters={"workspace": {"type": "string"}, "action": {"type": "string"}},
            engine_source="terraform"
        ),
        MCPToolDefinition(
            name="notion_workspace_sync",
            description="Interact with Notion pages, document databases, and team knowledge bases",
            parameters={"database_id": {"type": "string"}, "filter": {"type": "object"}},
            engine_source="notion"
        ),
        MCPToolDefinition(
            name="google_calendar_scheduler",
            description="Query availability, schedule meetings, and create calendar events",
            parameters={"event_title": {"type": "string"}, "start_time": {"type": "string"}},
            engine_source="google_calendar"
        ),
        MCPToolDefinition(
            name="gmail_message_handler",
            description="Search inbox, draft correspondence, and send authenticated emails",
            parameters={"recipient": {"type": "string"}, "subject": {"type": "string"}},
            engine_source="gmail"
        ),
        MCPToolDefinition(
            name="slack_notifier_bot",
            description="Post real-time notifications, thread replies, and alerts to Slack channels",
            parameters={"channel": {"type": "string"}, "message": {"type": "string"}},
            engine_source="slack"
        ),
        MCPToolDefinition(
            name="postgres_query_runner",
            description="Execute parameterized SQL queries and inspect schema definitions in PostgreSQL",
            parameters={"query": {"type": "string"}, "params": {"type": "array"}},
            engine_source="postgres"
        ),
        MCPToolDefinition(
            name="stripe_billing_sync",
            description="Query customer subscriptions, invoice statuses, and payment transactions",
            parameters={"customer_id": {"type": "string"}},
            engine_source="stripe"
        ),
        MCPToolDefinition(
            name="zendesk_ticket_agent",
            description="Fetch, create, update, and resolve customer support tickets",
            parameters={"ticket_id": {"type": "string"}, "status": {"type": "string"}},
            engine_source="zendesk"
        ),
        MCPToolDefinition(
            name="browser_web_navigator",
            description="Autonomous web browsing, DOM extraction, and visual navigation capabilities",
            parameters={"url": {"type": "string"}, "action": {"type": "string"}},
            engine_source="browser"
        ),
        MCPToolDefinition(
            name="openai_model_router",
            description="Route complex reasoning prompts and embeddings to external frontier models",
            parameters={"prompt": {"type": "string"}, "model": {"type": "string"}},
            engine_source="openai"
        ),
        MCPToolDefinition(
            name="datadog_apm_telemetry",
            description="Monitor application performance telemetry, traces, and latency percentiles",
            parameters={"service": {"type": "string"}, "timeframe": {"type": "string"}},
            engine_source="datadog"
        ),
        MCPToolDefinition(
            name="n8n_execute_webhook",
            description="Executes an active n8n automation webhook node",
            parameters={"workflow_id": {"type": "string"}, "payload": {"type": "object"}},
            engine_source="n8n"
        ),
        MCPToolDefinition(
            name="n8n_list_templates",
            description="Discover available pre-configured N8N automation workflow templates in the catalog",
            parameters={},
            engine_source="n8n"
        ),
        MCPToolDefinition(
            name="n8n_instantiate_template",
            description="Instantiate and deploy a pre-built N8N workflow template with custom parameters",
            parameters={"template_id": {"type": "string"}, "parameters": {"type": "object"}},
            engine_source="n8n"
        ),
        MCPToolDefinition(
            name="n8n_create_workflow",
            description="Synthesize, validate, and deploy a custom N8N automation workflow graph from an agent prompt",
            parameters={"prompt": {"type": "string"}, "name": {"type": "string"}},
            engine_source="n8n"
        ),
        MCPToolDefinition(
            name="n8n_list_active_workflows",
            description="Query and inspect active automated N8N workflows and webhook trigger URLs",
            parameters={},
            engine_source="n8n"
        ),
        MCPToolDefinition(
            name="langgraph_evaluate_drift",
            description="Evaluates token drift and state machine consistency across swarm actors",
            parameters={"state": {"type": "object"}},
            engine_source="langgraph"
        ),
        MCPToolDefinition(
            name="temporal_workflow_dispatcher",
            description="Start, signal, and query durable distributed workflows in Temporal",
            parameters={"workflow_type": {"type": "string"}, "args": {"type": "array"}},
            engine_source="temporal"
        ),
        MCPToolDefinition(
            name="activepieces_flow_trigger",
            description="Trigger automation pieces and execute integration workflows",
            parameters={"flow_id": {"type": "string"}, "data": {"type": "object"}},
            engine_source="activepieces"
        ),
        MCPToolDefinition(
            name="redis_pubsub_bus",
            description="Publish real-time events to distributed message channels in Redis",
            parameters={"channel": {"type": "string"}, "message": {"type": "string"}},
            engine_source="redis"
        ),
        MCPToolDefinition(
            name="e2b_sandbox_microvm",
            description="Spin up secure, isolated ephemeral microVMs for untrusted agent code execution",
            parameters={"template": {"type": "string"}, "timeout": {"type": "integer"}},
            engine_source="e2b"
        ),
    ]
    for tool in all_tools:
        broker_service.register_mcp_tool(tool)

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
