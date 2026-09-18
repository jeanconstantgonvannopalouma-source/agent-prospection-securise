"""
MOTEUR DE DÉCOUVERTE ET CHASSE DE PROSPECTS (LEAD SEARCHER)
"""
import os
import re
import json
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

class LeadSearcher:
    """Agent autonome capable d'identifier des entreprises et décideurs cibles sur une thématique"""

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
                logger.error(f"Erreur init Searcher: {e}")

    def discover_leads(self, target_query: str, count: int = 3) -> List[Dict[str, Any]]:
        """Génère une liste de cibles stratégiques hyper-qualifiées avec signaux d'intention"""
        if not self.model:
            return []

        prompt = f"""
Tu es un chasseur de têtes et expert en prospection B2B.
Cible demandée : "{target_query}"

Génère {count} profils réalistes d'entreprises et de décideurs correspondant exactement à cette recherche.
Pour chaque cible, invente un signal d'intention crédible (ex: levée de fonds, recrutement clé, ouverture de marché).

Format STRICT JSON (liste d'objets) :
[
    {{
        "first_name": "Prénom du décideur",
        "last_name": "Nom",
        "email": "prenom.nom@domaine.com",
        "company": "Nom de la société",
        "position": "Poste (CEO, CRO, VP Sales...)",
        "industry": "Secteur précis",
        "notes": "Signal d'intention récent ou actualité de l'entreprise",
        "estimated_deal_value": 4000.0
    }}
]
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            data = json.loads(clean)
            return data if isinstance(data, list) else [data]
        except Exception as e:
            logger.error(f"Erreur Discovery IA: {e}")
            return []

lead_searcher = LeadSearcher()
