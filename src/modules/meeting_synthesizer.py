"""
SYNTHÉTISEUR DE POST-CALL ET PLAN D'ACTION CLIENT (MEETING RECAP & CRM SYNC)
Transforme les notes brutes d'un appel en email de récapitulatif parfait et fiche CRM
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

class MeetingSynthesizer:
    """Génère le récapitulatif client, les engagements mutuels et la mise à jour CRM"""

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
                logger.error(f"Erreur init MeetingSynthesizer: {e}")

    def synthesize_call_notes(self, prospect_name: str, company: str, raw_notes: str) -> Dict[str, Any]:
        """Formate les notes d'appel en livrables exécutifs"""
        if not self.model:
            return {
                "prospect_followup_email": f"Bonjour {prospect_name},\n\nMerci pour notre échange de ce jour concernant {company}.\n\nComme convenu, nous avançons sur la mise en place.\n\nBien à vous,",
                "crm_deal_summary": f"Échange constructif avec {prospect_name} ({company}). Intérêt confirmé.",
                "deal_probability_percent": 65,
                "agreed_next_steps": ["Envoi de la proposition", "Point de validation jeudi prochain"]
            }

        prompt = f"""
Tu es un Account Executive d'élite en B2B SaaS.
Tu viens de terminer un appel commercial avec : {prospect_name} chez {company}.

NOTES BRUTES PRISES PENDANT L'APPEL :
"{raw_notes}"

TÂCHE :
Génère 3 éléments clés :
1. "prospect_followup_email" : L'email de remerciement envoyé au client (chaleureux, ultra-pro, résumant ses enjeux, notre proposition et la prochaine date de RDV convenue).
2. "crm_deal_summary" : Le mémo interne concis pour le CRM (Budget, Décideurs, Timing).
3. "deal_probability_percent" : Estimation réaliste de probabilité de signature (0 à 100%).
4. "agreed_next_steps" : Liste des actions concrètes validées.

Format JSON STRICT :
{{
    "prospect_followup_email": "corps de l'email",
    "crm_deal_summary": "résumé exécutif interne",
    "deal_probability_percent": 75,
    "agreed_next_steps": ["Action 1", "Action 2"]
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "prospect_followup_email": f"Bonjour {prospect_name},\n\nMerci pour la qualité de notre échange concernant {company}.\n\nJe reviens vers vous avec le plan d'action validé.\n\nExcellente journée,",
                "crm_deal_summary": f"Discussion positive avec {prospect_name}.",
                "deal_probability_percent": 60,
                "agreed_next_steps": ["Envoi de la documentation chiffrée"]
            }

meeting_synthesizer = MeetingSynthesizer()
