# OmniSwarm Automation Unified Platform

OmniSwarm is an open-source, enterprise-grade unified platform enabling users to deploy, orchestrate, and manage multi-agent swarms and workflow automation pipelines from a single interface (Mobile/iOS via Flutter, Backend via Kubernetes).

## Architecture Highlights
- **Dynamic Engine Broker (DEB)**: Unified abstraction layer translating canonical tasks to underlying upstream engines.
- **Model Context Protocol (MCP) Router**: Cross-engine tool discovery and bi-directional execution bus.
- **Sidecar Container Pattern**: Upstream frameworks run in decoupled sidecars for continuous upstream feature parity.
- **Sandboxed Execution**: Isolated microVMs (E2B / Daytona / gVisor) for secure untrusted code execution.
- **Dogfooding & Synthetic Media**: Autonomous testing swarms paired with Wan 2.1/2.7 and LivePortrait/MuseTalk media pipelines.

## Monorepo Layout
```
omniswarm/
├── apps/
│   ├── engine_broker/      # Core Dynamic Engine Broker (FastAPI + Async Dispatcher)
│   ├── mcp_router/         # MCP Tool & Resource Router
│   └── flutter_client/     # Flutter Cross-Platform Client
├── sidecars/
│   ├── agents/             # Agent framework sidecars (LangGraph, CrewAI, AutoGen, etc.)
│   └── workflows/          # Automation engine sidecars (n8n, Temporal, Activepieces, etc.)
├── deployments/
│   ├── docker-compose/     # Local development orchestration
│   ├── envoy/              # Envoy API Gateway configuration
│   └── k8s/                # Kubernetes Helm & GitOps manifests
└── scripts/                # Developer utilities and bootstrap scripts
```

## Quickstart (Development)

1. **Copy environment variables**:
   ```powershell
   cp .env.example .env
   ```

2. **Launch development stack**:
   ```powershell
   docker compose up -d
   ```

3. **Verify Broker Health**:
   ```bash
   curl http://localhost:8000/health
   ```
