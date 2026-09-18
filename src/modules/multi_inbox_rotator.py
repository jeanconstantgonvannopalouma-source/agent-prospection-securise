"""
GESTIONNAIRE & ROTATEUR MULTI-BOÎTES EMAIL (MULTI-INBOX ROTATOR)
"""
import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

INBOXES_FILE = os.path.join("data", "inboxes.json")

DEFAULT_INBOXES = [
    {"email": "jean.constant@pro-growth.fr", "sender_name": "Jean Constant", "daily_limit": 25, "sent_today": 8, "status": "ACTIVE 🟢"},
    {"email": "j.constant@consulting-b2b.fr", "sender_name": "Jean Constant", "daily_limit": 25, "sent_today": 12, "status": "ACTIVE 🟢"},
    {"email": "contact@jeanconstant-ia.fr", "sender_name": "Équipe Jean Constant", "daily_limit": 20, "sent_today": 3, "status": "ACTIVE 🟢"}
]

class MultiInboxRotator:
    """Gère la rotation des comptes d'expéditeurs pour maximiser la délivrabilité"""

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.inboxes = self.load_inboxes()

    def load_inboxes(self) -> List[Dict[str, Any]]:
        if os.path.exists(INBOXES_FILE):
            try:
                with open(INBOXES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        self.save_inboxes(DEFAULT_INBOXES)
        return DEFAULT_INBOXES

    def save_inboxes(self, data: List[Dict[str, Any]]) -> bool:
        try:
            with open(INBOXES_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.inboxes = data
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde inboxes: {e}")
            return False

    def get_next_available_inbox(self) -> Dict[str, Any]:
        """Sélectionne la boîte email optimale ayant du quota disponible"""
        for ib in self.inboxes:
            if ib.get("sent_today", 0) < ib.get("daily_limit", 25):
                ib["sent_today"] = ib.get("sent_today", 0) + 1
                self.save_inboxes(self.inboxes)
                return ib
        return self.inboxes[0] if self.inboxes else DEFAULT_INBOXES[0]

multi_inbox_rotator = MultiInboxRotator()
