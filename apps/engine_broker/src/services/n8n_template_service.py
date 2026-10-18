import os
import json
from typing import Dict, Any, List, Optional

class N8nTemplateService:
    """
    Manages the OmniSwarm library of pre-built N8N automation templates.
    """

    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            templates_dir = os.path.join(base_dir, "templates", "n8n")
        self.templates_dir = templates_dir
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.load_templates()

    def load_templates(self):
        self._cache.clear()
        if not os.path.exists(self.templates_dir):
            return

        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.templates_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        template_id = data.get("id") or filename.replace(".json", "")
                        self._cache[template_id] = data
                except Exception as e:
                    print(f"[N8nTemplateService] Failed to load template {filename}: {e}")

    def list_templates(self) -> List[Dict[str, Any]]:
        """Returns all templates with overview metadata."""
        summaries = []
        for t_id, t in self._cache.items():
            summaries.append({
                "id": t.get("id", t_id),
                "name": t.get("name", "Untitled Template"),
                "description": t.get("description", ""),
                "category": t.get("category", "General"),
                "trigger_type": t.get("trigger_type", "Webhook"),
                "nodes_count": t.get("nodes_count", len(t.get("workflow", {}).get("nodes", []))),
                "tags": t.get("tags", [])
            })
        return summaries

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Returns the full template object including workflow graph."""
        return self._cache.get(template_id)

    def instantiate_template(self, template_id: str, custom_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Renders a template workflow by injecting custom parameters and returning the N8N workflow payload.
        """
        template = self.get_template(template_id)
        if not template:
            return None

        workflow = json.loads(json.dumps(template.get("workflow", {})))

        # Append custom run suffix or adjust webhook path if needed
        run_name = custom_params.get("name")
        if run_name:
            workflow["name"] = run_name

        # Inject parameter substitutions across nodes
        webhook_path = custom_params.get("webhook_path")
        if webhook_path:
            for node in workflow.get("nodes", []):
                if node.get("type") == "n8n-nodes-base.webhook":
                    node.setdefault("parameters", {})["path"] = webhook_path

        return {
            "template_id": template_id,
            "name": workflow.get("name"),
            "workflow": workflow
        }

n8n_template_service = N8nTemplateService()
