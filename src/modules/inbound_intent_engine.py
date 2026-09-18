"""
CLASSIFICATEUR D'INTENTION INBOUND ET AUTO-REBOND
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

VALID_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest"
]

class InboundIntentEngine:
    """Analyse l'intention exacte d'une réponse client et prépare le rebond"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def classify_and_draft_reply(self, inbound_text: str, prospect_name: str = "Prospect", company: str = "l'Entreprise") -> Dict[str, Any]:
        if not self.api_key:
            return {
                "intent_category": "DEMANDE_RDV",
                "lead_temperature": "🔥 CHAUD",
                "recommended_crm_status": "RDV_PROPOSÉ",
                "draft_reply": f"Bonjour {prospect_name},\n\nMerci pour votre retour ! Auriez-vous une disponibilité ce jeudi à 14h30 ou vendredi à 10h pour un rapide échange ?\n\nBien à vous,"
            }

        genai.configure(api_key=self.api_key)
        prompt = f"""
Tu es un Account Executive d'élite en B2B.
Un prospect ({prospect_name} chez {company}) vient de répondre à notre email avec ce message :
"{inbound_text}"

TÂCHE :
1. Catégorise l'intention parmi :
   - "DEMANDE_RDV" (Veut un appel ou une démo)
   - "DEMANDE_INFO" (Demande une doc, un prix ou des précisions)
   - "OBJECTION_PRIX" (Trouve ça trop cher ou pas de budget)
   - "OBJECTION_TEMPS" (Pas le moment, rappelez plus tard)
   - "REFERRAL" (Redirige vers un collègue)
   - "REFUS" (Ne souhaite pas poursuivre)
2. Détermine la température du lead ("🔥 CHAUD", "🟡 TIÈDE", "⚪ FROID").
3. Rédige la réponse parfaite en 3 phrases max, professionnelle et courtoise.

Format JSON STRICT :
{{
    "intent_category": "DEMANDE_RDV",
    "lead_temperature": "🔥 CHAUD",
    "recommended_crm_status": "RDV_PROPOSÉ",
    "draft_reply": "Corps du mail de réponse"
}}
"""
        for model_name in VALID_MODELS:
            try:
                m = genai.GenerativeModel(model_name)
                resp = m.generate_content(prompt)
                clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
                return json.loads(clean)
            except Exception:
                continue

        return {
            "intent_category": "INTERESTED",
            "lead_temperature": "🔥 CHAUD",
            "recommended_crm_status": "EN_COURS",
            "draft_reply": f"Bonjour {prospect_name},\n\nMerci pour votre retour. Quand auriez-vous 10 minutes pour un rapide point ?\n\nBien à vous,"
        }

inbound_intent_engine = InboundIntentEngine()
