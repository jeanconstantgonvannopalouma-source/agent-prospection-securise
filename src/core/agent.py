"""
AGENT DE PROSPECTION STRATOSPHÉRIQUE - CHEF D'ORCHESTRE
"""
import logging
from typing import List, Dict, Any
from modules.prospect_finder import prospect_finder
from modules.message_engine import message_engine
from modules.email_sender import email_sender
from modules.objection_handler import objection_handler

logger = logging.getLogger(__name__)

class StratosphericAgent:
    """Agent autonome de prospection commerciale B2B"""

    def __init__(self):
        self.finder = prospect_finder
        self.engine = message_engine
        self.sender = email_sender
        self.objections = objection_handler

    def process_prospect(
        self,
        prospect_raw: Dict[str, Any],
        value_prop: str = "Automatisation de prospection B2B par IA haute conversion",
        framework: str = "PAS",
        auto_send: bool = False
    ) -> Dict[str, Any]:
        """
        Cycle complet sur un prospect :
        1. Enrichissement & Scoring ICP
        2. Copywriting IA sur-mesure
        3. Contrôle Qualité Anti-Spam
        4. Envoi (Simulé ou Réel)
        """
        # [1] Enrichissement
        enriched = self.finder.enrich_with_ai(prospect_raw)
        
        # [2] Génération du message
        generated = self.engine.generate_personalized_message(
            prospect=enriched,
            value_prop=value_prop,
            framework=framework
        )
        
        # [3] Contrôle qualité
        quality = self.engine.analyze_message_quality(
            generated.get("body", ""),
            generated.get("subject", "")
        )

        # [4] Envoi
        send_result = None
        if auto_send:
            send_result = self.sender.send_email(
                recipient_email=enriched.get("email", ""),
                subject=generated.get("subject", ""),
                body_text=generated.get("body", ""),
                prospect_name=enriched.get("first_name", "Prospect")
            )

        return {
            "prospect": enriched,
            "campaign_message": generated,
            "deliverability_analysis": quality,
            "send_status": send_result or {"mode": "ready_to_send"}
        }

agent = StratosphericAgent()
