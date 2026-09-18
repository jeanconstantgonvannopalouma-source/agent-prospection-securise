"""
RADAR D'INTENTION PAR LES OFFRES D'EMPLOI (HIRING INTENT RADAR)
Détecte les recrutements stratégiques pour synchroniser le timing de prospection
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

class HiringIntentRadar:
    """Analyse les recrutements en cours d'une entreprise pour déduire ses priorités immédiates"""

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
                logger.error(f"Erreur init HiringRadar: {e}")

    def analyze_hiring_signals(self, company_name: str, job_title_hiring: str = "Account Executive / SDR") -> Dict[str, Any]:
        """Déduit l'urgence et le point de friction lié à ce recrutement"""
        if not self.model:
            return {
                "detected_role_hiring": job_title_hiring,
                "underlying_pain": "Temps de formation et de ramp-up des nouvelles recrues",
                "hiring_hook": f"J'ai vu que vous recrutiez actuellement des {job_title_hiring} chez {company_name}."
            }

        prompt = f"""
Tu es un consultant en stratégie d'embauche et d'organisation commerciale.
Entreprise : {company_name}
Poste actuellement en recrutement : "{job_title_hiring}"

TÂCHE :
1. Quel défi immédiat ce recrutement révèle-t-il chez {company_name} ? (ex: besoin d'accélérer le chiffre, manque de leads pour les recrues, surcharge managériale).
2. Rédige l'accroche d'email parfaite reliant leur offre d'emploi à notre proposition de valeur (Accélération & Automatisation par IA).

Format STRICT JSON :
{{
    "detected_role_hiring": "{job_title_hiring}",
    "underlying_pain": "Le défi caché derrière cette embauche",
    "urgency_level": "Très Élevé (Phase active d'investissement)",
    "hiring_hook": "L'accroche citant l'offre de façon naturelle et percutante"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "detected_role_hiring": job_title_hiring,
                "underlying_pain": "Temps de montée en puissance",
                "urgency_level": "Élevé",
                "hiring_hook": f"J'ai vu votre offre d'emploi pour le poste de {job_title_hiring} chez {company_name}."
            }

hiring_radar = HiringIntentRadar()
