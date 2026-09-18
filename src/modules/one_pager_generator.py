"""
GÉNÉRATEUR DE PROPOSITION COMMERCIALE SUR-MESURE / ONE-PAGER (VIP PROPOSAL)
"""
import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

class OnePagerGenerator:
    """Génère un document de proposition stratégique ultra-personnalisé en Markdown"""

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
                logger.error(f"Erreur init OnePager: {e}")

    def generate_one_pager(self, prospect: Dict[str, Any], value_prop: str) -> str:
        """Rédige la proposition commerciale en Markdown complet"""
        p_name = prospect.get("first_name", "Décideur")
        p_company = prospect.get("company", "Entreprise")
        p_role = prospect.get("position", "Directeur")
        p_industry = prospect.get("industry", "B2B")
        p_notes = prospect.get("notes", "Expansion commerciale")

        if not self.model:
            return f"# Plan d'Action Stratégique pour {p_company}\n\nDocument généré pour {p_name}."

        prompt = f"""
Tu es un Senior Partner en Stratégie & Croissance Commerciale.
Rédige un One-Pager exécutif (Executive Summary) percutant et ultra-structuré pour :
- Destinataire : {p_name} ({p_role} chez {p_company})
- Secteur : {p_industry}
- Contexte : {p_notes}
- Notre Solution : {value_prop}

STRUCTURE ATTENDUE (au format Markdown élégant) :
1. 🎯 DIAGNOSTIC & GOULETS D'ÉTRANGLEMENT ACTUELS DE {p_company.upper()}
2. 💡 NOTRE APPROCHE SUR-MESURE & PROPOSITION DE VALEUR
3. 🚀 FEUILLE DE ROUTE D'IMPLÉMENTATION (Semaine 1 à Semaine 4)
4. 📊 RÉSULTATS CHIFFRÉS ATTENDUS (KPIs & ROI)
5. 🤝 PROCHAINE ÉTAPE RAPIDE

Rédige ce document avec un niveau de rigueur digne de McKinsey ou BCG, sans fioritures inutiles.
"""
        try:
            resp = self.model.generate_content(prompt)
            return resp.text.strip()
        except Exception as e:
            logger.error(f"Erreur génération OnePager: {e}")
            return f"# Proposition Stratégique - {p_company}\n\nDocument personnalisé en cours de finalisation."

one_pager_generator = OnePagerGenerator()
