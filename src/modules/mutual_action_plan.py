"""
GÉNÉRATEUR DE MUTUAL ACTION PLAN (PLAN DE DÉCISION PARTAGÉ)
Structure la feuille de route collaborative pour verrouiller les ventes B2B complexes
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

class MutualActionPlanGenerator:
    """Génère un plan de projet d'évaluation et de déploiement partagé"""

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
                logger.error(f"Erreur init MAP: {e}")

    def generate_map(self, prospect_name: str, company: str, target_go_live_days: int = 30) -> str:
        """Rédige un Mutual Action Plan en Markdown prêt à l'emploi"""
        if not self.model:
            return f"# Mutual Action Plan - {company}\n\nFeuille de route pour {prospect_name}."

        prompt = f"""
Tu es un Enterprise Sales Director.
Rédige un "Mutual Action Plan" (MAP) collaboratif et rassurant pour :
- Client : {company} (Porteur de projet : {prospect_name})
- Objectif : Go-Live réussi sous {target_go_live_days} jours
- Projet : Déploiement de notre Plateforme d'Intelligence Commerciale IA

STRUCTURE EXIGÉE (au format Markdown élégant) :
1. 🎯 OBJECTIFS D'AFFAIRES & CRITÈRES DE SUCCÈS MESURABLES (KPIs)
2. 👥 PARTIES PRENANTES & RÔLES (Sponsor Exécutif, Champion Métier, Sécurité IT, Juridique)
3. 🗓️ JALONNEMENT CHRONOLOGIQUE PAR PHASE :
   - Phase 1 : Cadrage & Alignement Sécurité / RGPD (Jours 1 à 7)
   - Phase 2 : Validation Technique & Intégration CRM (Jours 8 à 15)
   - Phase 3 : Validation Contractuelle & Signature (Jours 16 à 22)
   - Phase 4 : Onboarding des équipes & Go-Live (Jours 23 à 30)
4. 🚀 BÉNÉFICES DU RESPECT DU CALENDRIER
"""
        try:
            resp = self.model.generate_content(prompt)
            return resp.text.strip()
        except Exception:
            return f"# Mutual Action Plan - {company}\n\nCadrage du projet d'intégration IA pour {prospect_name}."

map_generator = MutualActionPlanGenerator()
