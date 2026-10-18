import os
import json
from typing import Dict, Any, List, Optional
from .workflow_builder_service import workflow_builder_service

class N8nTemplateService:
    """
    Manages the OmniSwarm library of pre-built N8N automation templates,
    including the comprehensive n8n Markets collection.
    """

    def __init__(self, templates_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        if templates_dir is None:
            templates_dir = os.path.join(base_dir, "templates", "n8n")
        self.templates_dir = templates_dir
        self.library_catalog_path = os.path.join(base_dir, "templates", "n8n_markets_library.json")
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.load_templates()

    def load_templates(self):
        self._cache.clear()

        # 1. Load standalone .json files in templates/n8n
        if os.path.exists(self.templates_dir):
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

        # 2. Load the rich n8n Markets catalog
        if os.path.exists(self.library_catalog_path):
            try:
                with open(self.library_catalog_path, "r", encoding="utf-8") as f:
                    market_items = json.load(f)
                    for item in market_items:
                        item_id = item.get("id")
                        if item_id and item_id not in self._cache:
                            self._cache[item_id] = item
            except Exception as e:
                print(f"[N8nTemplateService] Failed to load library catalog: {e}")

    def list_categories(self) -> List[str]:
        """Returns sorted list of all unique template categories."""
        cats = {t.get("category", "General") for t in self._cache.values()}
        return sorted(list(cats))

    def list_templates(self, category: Optional[str] = None, query: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns templates with overview metadata, with optional category, search query, and limit filters."""
        summaries = []
        q = (query or "").lower().strip()
        target_cat = (category or "").lower().strip()

        for t_id, t in self._cache.items():
            t_cat = t.get("category", "General")
            t_name = t.get("name", "Untitled Template")
            t_desc = t.get("description", "")
            t_tags = t.get("tags", [])

            # Category filter
            if target_cat and target_cat != "all" and t_cat.lower() != target_cat:
                continue

            # Query filter
            if q:
                match = (
                    q in t_id.lower() or
                    q in t_name.lower() or
                    q in t_desc.lower() or
                    any(q in str(tag).lower() for tag in t_tags)
                )
                if not match:
                    continue

            summaries.append({
                "id": t.get("id", t_id),
                "name": t_name,
                "description": t_desc,
                "category": t_cat,
                "trigger_type": t.get("trigger_type", "Webhook"),
                "nodes_count": t.get("nodes_count", len(t.get("workflow", {}).get("nodes", [])) or 4),
                "tags": t_tags
            })

        if limit and limit > 0:
            return summaries[:limit]
        return summaries

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Returns the full template object."""
        return self._cache.get(template_id)

    def instantiate_template(self, template_id: str, custom_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Renders a template workflow. If the template is from the catalog without a pre-baked
        graph, synthesizes a valid N8N workflow graph dynamically.
        """
        template = self.get_template(template_id)
        if not template:
            return None

        # Check if workflow graph exists, otherwise dynamically synthesize it
        if "workflow" in template and template["workflow"]:
            workflow = json.loads(json.dumps(template["workflow"]))
        else:
            prompt = template.get("description") or template.get("name")
            name = custom_params.get("name") or template.get("name")
            synthesized = workflow_builder_service.generate_workflow_from_prompt(prompt, name)
            workflow = synthesized["workflow"]

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
            "category": template.get("category", "General"),
            "workflow": workflow
        }

n8n_template_service = N8nTemplateService()
