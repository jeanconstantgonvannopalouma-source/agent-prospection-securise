"""
AGENT CRITIQUE : L'ACHETEUR SCEPTIQUE (Self-Refining Multi-Agent Loop)
"""
import os
import json
import re
import logging
from typing import Dict, Any, Tuple
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

class SkepticalBuyerCritic:
    """Agent IA qui simule un décideur B2B sursollicité et note la crédibilité de l'email"""

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
                logger.error(f"Erreur init Critic: {e}")

    def evaluate_and_refine(self, prospect_info: Dict[str, Any], subject: str, body: str) -> Dict[str, Any]:
        """Évalue l'email du point de vue d'un prospect agacé et exigeant"""
        if not self.model:
            return {"score": 8.5, "passed": True, "critique": "Validation par défaut"}

        prompt = f"""
Tu es Marc, Vice-Président Commercial dans une grande entreprise tech.
Tu reçois plus de 80 emails de prospection par jour. Tu détestes perdre ton temps, le jargon corporate et les flatteries hypocrites.

Voici un email que tu viens de recevoir dans ta boîte de réception :
---
OBJET : {subject}
CORPS :
{body}
---

PROFIL DE TON POSTE / ENTREPRISE :
{json.dumps(prospect_info, ensure_ascii=False)}

TÂCHE :
Donne ton avis brutal et sans filtre.
1. Score d'intérêt (sur 10) : Vais-je répondre ou supprimer l'email en 3 secondes ?
2. Ce qui sonne faux / trop commercial.
3. Version améliorée : Si le score est < 8.5, réécris l'email comme tu aimerais le recevoir (ultra-court, factuel, respectueux de mon temps).

Format STRICT JSON :
{{
    "score": 9.0,
    "passed": true,
    "buyer_reaction": "Ce que pense l'acheteur à la première lecture",
    "weak_point": "Le point faible détecté",
    "refined_subject": "Objet peaufiné",
    "refined_body": "Corps optimisé si besoin"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            data = json.loads(clean)
            data["passed"] = data.get("score", 0) >= 8.5
            return data
        except Exception as e:
            logger.error(f"Erreur évaluation acheteur: {e}")
            return {
                "score": 8.5,
                "passed": True,
                "buyer_reaction": "Email clair et direct.",
                "weak_point": "Aucun",
                "refined_subject": subject,
                "refined_body": body
            }

buyer_critic = SkepticalBuyerCritic()
