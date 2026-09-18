"""
MOTEUR POLYGLOTTE ET ADAPTATION CULTURELLE B2B (GLOBAL LOCALIZER)
Adapte le message aux codes d'affaires internationaux (US, UK, DE, ES, IT)
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

CULTURAL_FRAMEWORKS = {
    "EN_US": "Direct, axé sur les métriques concrètes (KPIs, ARR), CTA assertif, style concis et dynamique.",
    "EN_UK": "Poli, respectueux de l'étiquette, sous-entendu élégant, formule de politesse soignée.",
    "DE": "Très formel, vouvoiement strict (Sie), conformité technique, focus RGPD et robustesse sans superlatifs.",
    "ES": "Chaleureux, collaboratif, valorisation du partenariat de confiance et du potentiel mutuel.",
    "IT": "Élégant, relationnel, axé sur l'innovation et l'excellence opérationnelle."
}

class GlobalLocalizer:
    """Adapte et traduit un pitch commercial selon la culture d'affaires ciblée"""

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
                logger.error(f"Erreur init Localizer: {e}")

    def localize_message(self, french_subject: str, french_body: str, target_market: str = "EN_US") -> Dict[str, Any]:
        """Localise culturellement et linguistiquement l'email"""
        culture_guide = CULTURAL_FRAMEWORKS.get(target_market, CULTURAL_FRAMEWORKS["EN_US"])

        if not self.model:
            return {
                "target_market": target_market,
                "localized_subject": french_subject,
                "localized_body": french_body,
                "cultural_notes": "Mode direct standard"
            }

        prompt = f"""
Tu es un Senior VP of International Sales spécialisé dans l'expansion globale.
EMAIL SOURCE EN FRANÇAIS :
Sujet : {french_subject}
Corps :
{french_body}

MARCHÉ CIBLE : {target_market}
CODE CULTUREL DU MARCHÉ : {culture_guide}

TÂCHE :
Ne fais PAS une simple traduction mot à mot.
Réécris l'email pour qu'il semble avoir été rédigé nativement par le meilleur commercial local de ce pays.

Format STRICT JSON :
{{
    "target_market": "{target_market}",
    "localized_subject": "Sujet traduit et adapté",
    "localized_body": "Corps réécrit selon la culture locale",
    "cultural_notes": "Ce qui a été ajusté pour respecter les codes locaux"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "target_market": target_market,
                "localized_subject": f"Quick question regarding your growth",
                "localized_body": "Hi,\n\nI noticed your recent expansion and wanted to share how we help teams like yours accelerate pipeline.\n\nOpen for a brief 2-minute chat this week?\n\nBest,",
                "cultural_notes": "Traduction de secours"
            }

global_localizer = GlobalLocalizer()
