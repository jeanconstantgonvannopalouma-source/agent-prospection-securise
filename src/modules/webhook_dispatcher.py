"""
DISPATCHER DE WEBHOOKS EN 1 CLIC (WEBHOOK DISPATCHER)
"""
import json
import urllib.request
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WebhookDispatcher:
    """Pousse les prospects et campagnes vers des Webhooks externes (n8n, Make, Zapier)"""

    def dispatch_payload(self, webhook_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not webhook_url or not webhook_url.startswith("http"):
            return {"success": False, "error": "URL de Webhook invalide"}

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                code = resp.getcode()
                return {"success": code in [200, 201, 202, 204], "status_code": code}
        except Exception as e:
            logger.error(f"Erreur Webhook: {e}")
            return {"success": False, "error": str(e)}

webhook_dispatcher = WebhookDispatcher()
