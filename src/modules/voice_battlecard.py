"""
GÉNÉRATEUR DE BATTLECARD D'APPEL TÉLÉPHONIQUE (COLD CALLING BATTLECARD)
"""
import os
import json
import re
import logging
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

class VoiceBattlecardGenerator:
    """Génère un script d'appel téléphonique et une matrice de riposte vocale"""

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
                logger.error(f"Erreur init Battlecard: {e}")

    def generate_battlecard(self, prospect: Dict[str, Any], value_prop: str) -> Dict[str, Any]:
        """Génère la structure complète pour un appel téléphonique à froid"""
        p_name = prospect.get("first_name", "le Prospect")
        p_company = prospect.get("company", "l'Entreprise")
        p_role = prospect.get("position", "Décideur")
        p_notes = prospect.get("notes", "Croissance commerciale")

        if not self.model:
            return {
                "opener_7_seconds": f"Bonjour {p_name}, je sais que je vous interromps dans votre journée chez {p_company}. Avez-vous 30 secondes ?",
                "elevator_pitch": "Nous aidons les dirigeants à doubler leurs prises de RDV qualifiés par IA.",
                "qualifying_question": "Comment gérez-vous votre prospection sortante actuellement ?",
                "objection_pas_le_temps": "C'est exactement pour cela que je vous appelle : vous faire gagner 10h/semaine.",
                "cta_close": "Faisons un point de 10 min mardi à 10h ou jeudi à 14h ?"
            }

        prompt = f"""
Tu es le meilleur coach mondial en Cold Calling B2B (prospection téléphonique).
Cible : {p_name} ({p_role} chez {p_company}).
Signal d'actualité : {p_notes}.
Notre solution : {value_prop}.

TÂCHE :
Génère une battlecard téléphonique percutante et anti-rejet :
1. "opener_7_seconds" : Accroche téléphonique directe, polie et désarmante (zéro ton commercial faux).
2. "elevator_pitch_15_sec" : Le pitch d'impact en 2 phrases max.
3. "qualifying_question" : La question ouverte qui fait parler le prospect de ses vrais défis.
4. "objection_already_have_tool" : Riposte si le prospect dit : "On a déjà ce qu'il faut".
5. "objection_send_email" : Riposte si le prospect dit : "Envoyez-moi un mail" (le piège classique).
6. "meeting_close" : La formulation exacte pour verrouiller la date du RDV.

Format STRICT JSON :
{{
    "opener_7_seconds": "texte",
    "elevator_pitch_15_sec": "texte",
    "qualifying_question": "texte",
    "objection_already_have_tool": "texte",
    "objection_send_email": "texte",
    "meeting_close": "texte"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "opener_7_seconds": f"Bonjour {p_name}, je sais que vous êtes très occupé chez {p_company}. Je vous promets d'être bref.",
                "elevator_pitch_15_sec": f"Nous automatisons l'acquisition commerciale de comptes comme {p_company}.",
                "qualifying_question": "Quel est votre plus gros goulet d'étranglement pour générer des opportunités ce trimestre ?",
                "objection_already_have_tool": "Totalement compréhensible. La plupart de nos clients utilisaient déjà une solution avant de découvrir notre gain de +35% de conversion.",
                "objection_send_email": "Je vais vous l'envoyer avec plaisir. Pour que je cible l'info exacte : est-ce que votre priorité est le volume ou la qualification ?",
                "meeting_close": "Seriez-vous disponible 10 minutes ce jeudi à 14h30 ?"
            }

voice_battlecard = VoiceBattlecardGenerator()
