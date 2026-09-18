"""
MOTEUR ABM SYNDICATE (ACCOUNT-BASED MARKETING MULTI-CONTACTS)
Orchestre des attaques coordonnées sur 3 décideurs clés de la même entreprise
"""
import os
import re
import json
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

class ABMSyndicate:
    """Génère une campagne multi-décideurs pour une entreprise cible"""

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
                logger.error(f"Erreur init ABM: {e}")

    def generate_abm_campaign(self, company_name: str, industry: str, news_trigger: str, value_prop: str) -> Dict[str, Any]:
        """Génère 3 approches complémentaires pour le CEO, le VP Sales et le RevOps"""
        if not self.model:
            return {
                "company": company_name,
                "strategy": "Approche tri-angulaire standard",
                "economic_buyer": {"role": "CEO", "subject": f"Vision {company_name}", "angle": "Croissance"},
                "champion": {"role": "VP Sales", "subject": f"Pipeline {company_name}", "angle": "RDVs"},
                "influencer": {"role": "RevOps", "subject": f"Stack {company_name}", "angle": "Automatisation"}
            }

        prompt = f"""
Tu es le directeur d'une agence de prospection ABM (Account-Based Marketing) de niveau mondial.
ENTREPRISE CIBLE : {company_name} (Secteur : {industry})
SIGNAL D'ACTUALITÉ : {news_trigger}
NOTRE SOLUTION : {value_prop}

TÂCHE :
Génère une stratégie d'encerclement en 3 angles distincts pour toucher les 3 parties prenantes simultanément :
1. "economic_buyer" (CEO / CFO) : Pitch macro-économique, ROI, marge et valorisation.
2. "champion" (VP Sales / Head of Sales) : Pitch opérationnel, quotas de l'équipe, temps gagné.
3. "revops_influencer" (Head of RevOps / CTO) : Pitch technique, synchronisation CRM, propreté des données.

Format STRICT JSON :
{{
    "company": "{company_name}",
    "abm_core_narrative": "Le fil conducteur de la campagne",
    "economic_buyer": {{
        "target_role": "CEO / Directeur Général",
        "subject": "objet percutant",
        "body": "email ultra-court",
        "key_metric": "Ex: +120k€ pipeline/mois"
    }},
    "champion": {{
        "target_role": "VP Sales / Head of Commercial",
        "subject": "objet percutant",
        "body": "email ultra-court",
        "key_metric": "Ex: 15h gagnées/SDR/semaine"
    }},
    "revops_influencer": {{
        "target_role": "Head of RevOps / Ops",
        "subject": "objet percutant",
        "body": "email ultra-court",
        "key_metric": "Ex: 0 doublon, synchro API"
    }}
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "company": company_name,
                "abm_core_narrative": "Accélération commerciale B2B",
                "economic_buyer": {"target_role": "CEO", "subject": f"Croissance {company_name}", "body": "Bonjour,\n\nAccélérons vos résultats ce trimestre.", "key_metric": "+30% CA"},
                "champion": {"target_role": "VP Sales", "subject": f"Quotas {company_name}", "body": "Bonjour,\n\nFournissons plus de RDVs à vos SDRs.", "key_metric": "+40% RDVs"},
                "revops_influencer": {"target_role": "RevOps", "subject": f"Process {company_name}", "body": "Bonjour,\n\nAutomatisons vos enrichissements.", "key_metric": "100% CRM sync"}
            }

abm_syndicate = ABMSyndicate()
