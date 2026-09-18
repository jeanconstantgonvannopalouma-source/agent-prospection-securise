"""
ANALYSEUR DE PROFIL LINKEDIN ET TRAJECTOIRE DE CARRIÈRE (LINKEDIN ANALYZER)
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

class LinkedInAnalyzer:
    """Analyse la trajectoire professionnelle d'un prospect pour déduire des points de connivence"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = None
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                for candidate in ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest"]:
                    try:
                        self.model = genai.GenerativeModel(candidate)
                        break
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"Erreur init LinkedInAnalyzer: {e}")

    def analyze_career_path(self, career_text: str) -> Dict[str, Any]:
        """Extrait les moments clés et crée l'accroche relationnelle"""
        if not self.model:
            return {
                "key_highlight": "Promotion ou expérience récente marquante",
                "rapport_hook": f"J'ai remarqué votre parcours impressionnant et votre évolution récente."
            }

        prompt = f"""
Tu es un expert en networking d'affaires B2B.
Voici le résumé du profil / parcours LinkedIn d'un prospect :
"{career_text}"

TÂCHE :
1. Identifie l'élément le plus marquant de son parcours (ex: 'Ex-McKinsey', 'Promotion récente comme VP Sales', 'Fondateur ayant revendu sa précédente boîte').
2. Rédige une phrase de connivence relationnelle ultra-naturelle (15 mots max) à placer au tout début d'un email de prospection.

Format JSON STRICT :
{{
    "key_highlight": "Résumé de l'élément fort",
    "rapport_hook": "Phrase d'accroche relationnelle"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "key_highlight": "Parcours B2B solide",
                "rapport_hook": "Impressionné par vos récents succès et la trajectoire de votre équipe."
            }

linkedin_analyzer = LinkedInAnalyzer()
