"""
GESTIONNAIRE D'OBJECTIONS PAR IA
"""
import logging
from typing import Dict, Any
from modules.message_engine import message_engine

logger = logging.getLogger(__name__)

class ObjectionHandler:
    """Interprète et désamorce les objections commerciales"""

    def handle(self, prospect: Any, objection_text: str) -> Dict[str, Any]:
        """Génère la réponse de recadrage appropriée"""
        logger.info(f"🛡️ Traitement d'objection reçue : '{objection_text[:50]}...'")
        return message_engine.generate_objection_response(prospect, objection_text)

objection_handler = ObjectionHandler()
