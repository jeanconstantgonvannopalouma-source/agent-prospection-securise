"""
TRACKER DE LEVÉES DE FONDS ET SIGNAUX CAPITAL-RISQUE (VC FUNDING TRACKER)
Détecte la maturité d'investissement et formule le pitch de capital allocation
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

class VCFundingTracker:
    """Analyse les levées de fonds pour caler le pitch sur les attentes des investisseurs"""

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
                logger.error(f"Erreur init VCFunding: {e}")

    def analyze_funding_context(self, company_name: str, round_type: str = "Série A (5M€ - Eurazeo/Kima)", target_role: str = "CEO") -> Dict[str, Any]:
        """Déduit la pression exercée par les fonds investisseurs et formule l'argumentaire"""
        if not self.model:
            return {
                "funding_stage": round_type,
                "investor_pressure_point": "Exigence de croissance rapide du chiffre d'affaires et contrôle du CAC",
                "funding_angle": f"Accélérer le go-to-market post-{round_type}",
                "pitch_hook": f"Félicitations pour votre tour de table ({round_type}). Les prochains mois sont décisifs pour accélérer votre pipeline."
            }

        prompt = f"""
Tu es un Partner en Venture Capital et spécialiste du Go-To-Market post-funding.
Entreprise : {company_name}
Tour de table / Levée de fonds : "{round_type}"
Interlocuteur ciblé : {target_role}

TÂCHE :
1. Quelle est l'obsession #1 des investisseurs pour cette entreprise après ce tour ({round_type}) ? (ex: prouver la scalabilité, conquérir l'international, rentabiliser le coût d'acquisition).
2. Rédige l'accroche ultra-légitime reliant leur levée de fonds à notre plateforme d'accélération IA sans sonner opportuniste ou maladroit.

Format STRICT JSON :
{{
    "funding_stage": "{round_type}",
    "board_expectation": "L'attente principale du Conseil d'Administration / Investisseurs",
    "growth_bottleneck": "Le risque majeur qui menace leur rentabilité post-levée",
    "pitch_hook": "L'accroche citant la levée de fonds avec une élégance chirurgicale"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "funding_stage": round_type,
                "board_expectation": "Accélération du pipeline commercial",
                "growth_bottleneck": "Temps de ramp-up des commerciaux",
                "pitch_hook": f"Félicitations pour l'annonce de votre tour ({round_type}) chez {company_name}."
            }

vc_funding_tracker = VCFundingTracker()
