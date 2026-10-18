# OmniSwarm Unified Platform – Product & Integration Suite

## 1. Product Requirements Document (PRD)

### Project Overview
OmniSwarm is a unified control plane designed to orchestrate and manage complex multi-agent systems. It acts as a central hub (Dynamic Engine Broker) that allows users to deploy, monitor, and connect multiple AI agent frameworks simultaneously within a single, highly transparent interface.

### Core Objectives
*   **Centralization:** Eliminate tool fragmentation by providing a unified dashboard for all agent swarms.
*   **Interoperability:** Seamlessly connect external systems and data using standard protocols.
*   **Transparency:** Provide real-time observability into the execution state and logic of AI agents.

### Target Features
*   **Unified Control Plane:** A dashboard to access Control Plane, Agent Swarms, Live Stream, and MCP Registry.
*   **Dynamic Framework Deployment:** Support for diverse engines including LangGraph, CrewAI, Agno, MetaGPT, ChatDev, Smolagents, and Mastra.
*   **Live Stream Execution Logging:** Real-time visibility into agent activities, node initialization, task progression, and final artifact compilation.
*   **Cross-platform MCP Bus:** An extensible Tool Bus architecture using the Model Context Protocol (MCP) to register external services and tools.

---

## 2. Standard Operating Procedure (SOP) – Swarm Operations & Integrations

### Objective
This SOP outlines the standard procedures for dispatching swarms and registering external Model Context Protocol (MCP) servers within the OmniSwarm platform.

### Procedure A: Dispatching a Swarm
1.  **Navigate:** Go to the "Agent Swarms" tab from the top navigation bar.
2.  **Select Framework:** Locate the desired agent framework (e.g., CrewAI) and click the corresponding "Launch" button.
3.  **Configure Parameters:**
    *   **Swarm Run Name:** Enter a unique identifier for the swarm run.
    *   **Initial Goal / Mission Prompt:** Enter a detailed, structured mission prompt describing the swarm’s roles, tasks, and expected deliverables.
4.  **Execute:** Click the "Launch Swarm" button to initiate the process.
5.  **Monitor:** Navigate to the "Live Stream" tab to observe the execution logs in real-time as the broker dispatches the swarm and the agents complete the tasks.

### Procedure B: Registering External MCP Servers
1.  **Navigate:** Go to the "MCP Registry" tab in the top navigation bar.
2.  **Add Server:** Locate the option to add or register a new MCP server.
3.  **Input Details:**
    *   **Tool Name:** Enter the identifying name of the service/tool.
    *   **Engine Source:** Specify the origin or protocol type (e.g., N8N, LANGGRAPH, GITHUB).
    *   **Description:** Add a brief summary of the tool's functionality.
4.  **Verify & Test:** Once registered, the tool will appear in the MCP Tool Bus list, where you can verify the connection (e.g., clicking "Test Invoke").

---

## 3. Step-by-Step Integration Tutorial – Expanding Capabilities

To achieve maximal compatibility with external workflows, you must register the full suite of MCP-compatible servers. Follow this tutorial to integrate all twenty essential platforms.

### Step 1: Access the Registry
1.  Log in to the OmniSwarm Unified Platform.
2.  Click on the **"MCP Registry"** link in the header navigation.

### Step 2: Register Development & Infrastructure Tools
Add the following core developer and infrastructure tools to the registry:
1.  **GitHub:** Connect for accessing repositories, pulling code, and managing issues.
    * Tool: `github_repo_manager`
    * Engine Source: `GITHUB`
2.  **Docker:** Register to oversee container operations and statuses.
    * Tool: `docker_container_ops`
    * Engine Source: `DOCKER`
3.  **Kubernetes:** Connect to manage cluster operations and orchestration.
    * Tool: `kubernetes_cluster_ops`
    * Engine Source: `KUBERNETES`
4.  **Terraform:** Register for full-lifecycle infrastructure-as-code management.
    * Tool: `terraform_iac_manager`
    * Engine Source: `TERRAFORM`

### Step 3: Register Productivity & Communication Tools
Integrate your daily productivity and collaboration applications:
5.  **Notion:** Add to allow agents to interact with pages, databases, and notes.
    * Tool: `notion_workspace_sync`
    * Engine Source: `NOTION`
6.  **Google Calendar:** Register to enable agents to schedule events and meetings.
    * Tool: `google_calendar_scheduler`
    * Engine Source: `GOOGLE_CALENDAR`
7.  **Gmail:** Connect for monitoring, drafting, or sending emails.
    * Tool: `gmail_message_handler`
    * Engine Source: `GMAIL`
8.  **Slack:** Add for team communications and automating notifications.
    * Tool: `slack_notifier_bot`
    * Engine Source: `SLACK`

### Step 4: Register Data & External Services
Connect essential data platforms and service endpoints:
9.  **Postgres:** Integrate for executing queries and managing relational database data.
    * Tool: `postgres_query_runner`
    * Engine Source: `POSTGRES`
10. **Stripe:** Register to handle payment operations and subscription data.
    * Tool: `stripe_billing_sync`
    * Engine Source: `STRIPE`
11. **Zendesk:** Connect to allow agents to read and manage customer support tickets.
    * Tool: `zendesk_ticket_agent`
    * Engine Source: `ZENDESK`

### Step 5: Register Advanced AI & Browsing Capabilities
Add specialized reasoning and web navigation tools:
12. **Browser:** Register the web-browsing tool to give agents internet access and visual navigation.
    * Tool: `browser_web_navigator`
    * Engine Source: `BROWSER`
13. **OpenAI Server:** Connect external language models to expand reasoning capabilities.
    * Tool: `openai_model_router`
    * Engine Source: `OPENAI`
14. **Datadog:** Add for comprehensive application performance monitoring.
    * Tool: `datadog_apm_telemetry`
    * Engine Source: `DATADOG`

---

### Step 6: Register the Complete MCP Tool Bus
Ensure your system mirrors the comprehensive MCP bus capabilities by reviewing the registry for exact mappings to tools such as:
15. `n8n_execute_webhook` (Engine Source: NBN / N8N) – To execute active n8n automation nodes.
16. `langgraph_evaluate_drift` (Engine Source: LANGGRAPH) – To natively evaluate token drift and state consistency.
17. `temporal_workflow_dispatcher` (Engine Source: TEMPORAL) – Start, signal, and query durable distributed workflows.
18. `activepieces_flow_trigger` (Engine Source: ACTIVEPIECES) – Trigger automation pieces and execute integration workflows.
19. `redis_pubsub_bus` (Engine Source: REDIS) – Publish real-time events to distributed message channels in Redis.
20. `e2b_sandbox_microvm` (Engine Source: E2B) – Spin up secure, isolated ephemeral microVMs for untrusted agent code execution.

*Note: All 20 integrations are registered into the OmniSwarm Engine Broker startup event and accessible via the Model Context Protocol (MCP) tool bus API (`/api/v1/mcp/tools`) and interactive UI.*
