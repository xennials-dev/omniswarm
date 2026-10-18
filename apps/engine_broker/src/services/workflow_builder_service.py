import re
import uuid
import json
from typing import Dict, Any, List, Tuple

class WorkflowBuilderService:
    """
    Synthesizes and validates production N8N workflow graphs for AI agents and users.
    """

    def generate_workflow_from_prompt(self, prompt: str, name: str = None) -> Dict[str, Any]:
        """
        Synthesizes a valid N8N workflow JSON graph from natural language instruction.
        """
        p_lower = prompt.lower()
        wf_id = str(uuid.uuid4())[:8]
        wf_name = name or self._derive_workflow_name(prompt)

        nodes: List[Dict[str, Any]] = []
        connections: Dict[str, Any] = {}
        x_pos = 240
        y_pos = 300
        spacing = 240

        # 1. Determine Trigger Node
        is_scheduled = any(k in p_lower for k in ["every", "cron", "hourly", "daily", "scheduled", "poll", "interval"])
        if is_scheduled:
            trigger_node = {
                "parameters": {
                    "rule": {
                        "interval": [{"field": "minutes", "minutesInterval": 15}]
                    }
                },
                "id": f"node_trigger_{wf_id}",
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [x_pos, y_pos]
            }
        else:
            slug = re.sub(r'[^a-z0-9]+', '-', wf_name.lower()).strip('-')[:24]
            trigger_node = {
                "parameters": {
                    "httpMethod": "POST",
                    "path": f"agent-{slug}",
                    "responseMode": "onReceived"
                },
                "id": f"node_trigger_{wf_id}",
                "name": "Incoming Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [x_pos, y_pos],
                "webhookId": f"wh-{slug}"
            }
        nodes.append(trigger_node)
        prev_node_name = trigger_node["name"]

        # 2. Logic / Transformation Node
        x_pos += spacing
        transform_node = {
            "parameters": {
                "jsCode": (
                    "// Synthesized Agent Transformer\n"
                    "const input = $input.first().json;\n"
                    "return [{\n"
                    "  json: {\n"
                    "    processed_at: new Date().toISOString(),\n"
                    "    raw_payload: input,\n"
                    f"    workflow_context: '{wf_name}'\n"
                    "  }\n"
                    "}];"
                )
            },
            "id": f"node_transform_{wf_id}",
            "name": "Format & Validate Payload",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [x_pos, y_pos]
        }
        nodes.append(transform_node)
        connections[prev_node_name] = {"main": [[{"node": transform_node["name"], "type": "main", "index": 0}]]}
        prev_node_name = transform_node["name"]

        # 3. Action Nodes Based on Entities Detected in Prompt
        actions = []
        if any(k in p_lower for k in ["slack", "alert", "notify", "channel"]):
            actions.append(("slack", "Post Slack Alert", "http://engine-broker:8000/api/v1/mcp/tools/slack_notifier_bot/invoke", {"channel": "#swarms", "message": "={{ '🚨 Alert: ' + JSON.stringify($json) }}"}))
        if any(k in p_lower for k in ["github", "issue", "pr", "repo", "commit"]):
            actions.append(("github", "Triage GitHub Code", "http://engine-broker:8000/api/v1/mcp/tools/github_repo_manager/invoke", {"repo": "xennials-dev/omniswarm", "action": "analyze_issue"}))
        if any(k in p_lower for k in ["postgres", "database", "sql", "table", "db"]):
            actions.append(("postgres", "Execute Database Query", "http://engine-broker:8000/api/v1/mcp/tools/postgres_query_runner/invoke", {"query": "SELECT * FROM executions LIMIT 1", "params": []}))
        if any(k in p_lower for k in ["stripe", "payment", "billing", "charge"]):
            actions.append(("stripe", "Sync Stripe Record", "http://engine-broker:8000/api/v1/mcp/tools/stripe_billing_sync/invoke", {"customer_id": "cus_agent_stream"}))
        if any(k in p_lower for k in ["browser", "scrape", "crawl", "web page"]):
            actions.append(("browser", "Scrape Target Webpage", "http://engine-broker:8000/api/v1/mcp/tools/browser_web_navigator/invoke", {"url": "https://news.ycombinator.com", "action": "scrape"}))
        if any(k in p_lower for k in ["openai", "gpt", "summarize", "llm", "reasoning", "model"]):
            actions.append(("openai", "Frontier LLM Reasoning", "http://engine-broker:8000/api/v1/mcp/tools/openai_model_router/invoke", {"prompt": f"Synthesized analysis for: {prompt}", "model": "gpt-4o"}))
        if any(k in p_lower for k in ["drift", "langgraph", "checkpoint", "consistency"]):
            actions.append(("langgraph", "Drift Evaluation Probe", "http://engine-broker:8000/api/v1/mcp/tools/langgraph_evaluate_drift/invoke", {"state": {"prompt": prompt}}))

        # Default fallback action: Dispatch Swarm
        if not actions:
            actions.append(("swarm", "Dispatch Autonomous Swarm", "http://engine-broker:8000/api/v1/swarms/kickoff", {
                "name": f"Agent Swarm: {wf_name}",
                "engine": "langgraph",
                "initial_prompt": prompt,
                "roles": [{"role": "Orchestrator", "goal": "Execute automated workflow"}]
            }))

        for action_key, action_name, url, body in actions:
            x_pos += spacing
            body_lines = []
            for k, v in body.items():
                if isinstance(v, str) and v.startswith("={{"):
                    body_lines.append(f'  "{k}": {v}')
                else:
                    body_lines.append(f'  "{k}": {json.dumps(v)}')
            json_body_str = "={\n" + ",\n".join(body_lines) + "\n}"

            action_node = {
                "parameters": {
                    "method": "POST",
                    "url": url,
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": json_body_str
                },
                "id": f"node_{action_key}_{wf_id}",
                "name": action_name,
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [x_pos, y_pos]
            }
            nodes.append(action_node)
            connections[prev_node_name] = {"main": [[{"node": action_name, "type": "main", "index": 0}]]}
            prev_node_name = action_name

        workflow_obj = {
            "name": wf_name,
            "nodes": nodes,
            "connections": connections,
            "active": True,
            "settings": {
                "executionOrder": "v1"
            }
        }

        return {
            "workflow_id": wf_id,
            "name": wf_name,
            "prompt": prompt,
            "nodes_count": len(nodes),
            "workflow": workflow_obj
        }

    def _derive_workflow_name(self, prompt: str) -> str:
        words = prompt.strip().split()
        if len(words) <= 5:
            return prompt.title()
        return " ".join(words[:5]).title() + " Flow"

    def validate_workflow(self, workflow: Dict[str, Any]) -> Tuple[bool, str]:
        if not isinstance(workflow, dict):
            return False, "Workflow must be a JSON dictionary"
        nodes = workflow.get("nodes", [])
        if not nodes:
            return False, "Workflow has no nodes"

        node_names = {n.get("name") for n in nodes if "name" in n}
        connections = workflow.get("connections", {})
        for src, conn_data in connections.items():
            if src not in node_names:
                return False, f"Connection references unknown source node: '{src}'"
            for branch in conn_data.get("main", []):
                for dest in branch:
                    dest_node = dest.get("node")
                    if dest_node not in node_names:
                        return False, f"Connection references unknown destination node: '{dest_node}'"
        return True, "Valid N8N workflow graph"

workflow_builder_service = WorkflowBuilderService()
