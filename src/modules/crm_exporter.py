"""
CONNECTEUR DE SYNCHRONISATION EXTERNE & WEBHOOKS (CRM EXPORTER)
Permet d'envoyer les leads vers Notion, HubSpot, n8n, Make ou Zapier
"""
import os
import json
import urllib.request
import logging
from typing import Dict, Any, List
from modules.pipeline_tracker import pipeline_tracker

logger = logging.getLogger(__name__)

class CRMExporter:
    """Gère l'export et l'envoi HTTP de leads vers des CRM tiers"""

    def export_to_json(self, output_filename: str = "data/pipeline_export.json") -> str:
        """Exporte l'ensemble du CRM dans un fichier JSON universel"""
        stats = pipeline_tracker.get_stats()
        export_data = {
            "exported_at": os.popen("date /t").read().strip(),
            "pipeline_summary": stats,
            "prospects": stats.get("recent_prospects", [])
        }
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        return output_filename

    def send_to_webhook(self, webhook_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie un lead ou un rapport complet à un Webhook (n8n, Make, Zapier)"""
        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                status_code = resp.getcode()
                return {"success": status_code in [200, 201, 204], "status_code": status_code}
        except Exception as e:
            return {"success": False, "error": str(e)}

crm_exporter = CRMExporter()
