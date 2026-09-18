"""
CLASSIFICATEUR ET RÉPONDEUR AUTOMATIQUE DE RÉPONSES ENTRANTES (INBOUND TRIAGE)
"""
import os
import re
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

class InboundReplyTriage:
    """Analyse l'intention d'un prospect ayant répondu et pilote la suite du cycle de vente"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = None
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                for candidate in ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest"]:
                    try:
                        self.model = genai.GenerativeModel(candidate)
                        break
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"Erreur init Triage: {e}")

    def analyze_reply(self, prospect_info: Dict[str, Any], reply_text: str) -> Dict[str, Any]:
        """Classifie le message reçu et génère le plan d'action immédiat"""
        if not self.model:
            return {
                "category": "INTERESTED",
                "sentiment_score": 8,
                "summary": "Le prospect semble ouvert à la discussion.",
                "action_required": "PROPOSER_RDV",
                "suggested_reply": "Super ! Seriez-vous disponible ce jeudi à 14h ?"
            }

        prompt = f"""
Tu es un Directeur des Opérations Commerciales B2B de haut niveau.
Un prospect vient de répondre à notre campagne de prospection.

PROSPECT : {json.dumps(prospect_info, ensure_ascii=False)}
MESSAGE DU PROSPECT :
"{reply_text}"

TÂCHE :
1. Catégorise STRICTEMENT la réponse parmi :
   - "POSITIVE_LEAD" (Intéressé, demande des infos, veut un appel)
   - "OBJECTION" (Pas le temps, a déjà un prestataire, trouve ça cher, etc.)
   - "UNSUBSCRIBE" (Ne veut plus être contacté, pas intéressé du tout)
   - "OUT_OF_OFFICE" (Message d'absence automatique)
   - "REFERRAL" (Redirige vers un collègue / autre décideur)

2. Note la chaleur du lead (1 à 10).
3. Rédige la réponse immédiate recommandée (ultra-courte et efficace).

Format STRICT JSON :
{{
    "category": "POSITIVE_LEAD",
    "sentiment_score": 9,
    "intent_summary": "Explication en 1 phrase de ce que veut le prospect",
    "crm_status_to_apply": "RDV_DEMANDE / OBJECTION / DESINSCRIT / EN_ATTENTE",
    "suggested_reply": "Corps de la réponse prêt à être envoyé"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception as e:
            logger.error(f"Erreur Triage IA: {e}")
            return {
                "category": "POSITIVE_LEAD",
                "sentiment_score": 7,
                "intent_summary": "Réponse reçue",
                "crm_status_to_apply": "REPONDU",
                "suggested_reply": "Merci pour votre retour ! Quand auriez-vous un créneau pour en discuter ?"
            }

reply_triage = InboundReplyTriage()
