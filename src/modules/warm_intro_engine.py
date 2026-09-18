"""
MOTEUR DE WARM INTRO ET MESSAGES TRANSFÉRABLES (FORWARDABLE BLURBS)
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

class WarmIntroEngine:
    """Rédige des demandes d'introduction et des e-mails transférables (Forwardable Blurbs)"""

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
                logger.error(f"Erreur init WarmIntro: {e}")

    def generate_forwardable_intro(self, mutual_contact_name: str, target_name: str, target_company: str, value_prop: str) -> Dict[str, Any]:
        """Génère la demande d'intro + le blurb transférable"""
        if not self.model:
            return {
                "ask_to_connector": f"Bonjour {mutual_contact_name}, aurais-tu la possibilité de me mettre en relation avec {target_name} chez {target_company} ? Voici un texte tout prêt ci-dessous.",
                "forwardable_blurb": f"Hello {target_name}, je te transfère ce message de notre part concernant l'automatisation commerciale pour {target_company}."
            }

        prompt = f"""
Tu es un expert en networking d'affaires B2B de haut niveau.
Intermédiaire / Connecteur : {mutual_contact_name}
Cible finale : {target_name} chez {target_company}
Notre offre : {value_prop}

TÂCHE :
Génère 2 messages coordonnés :
1. "ask_to_connector" : Le message courtois envoyé à l'intermédiaire pour lui demander s'il accepterait de faire l'intro (zéro gêne, respect de son temps).
2. "forwardable_blurb" : Le paragraphe autonome que l'intermédiaire n'a plus qu'à transférer directement à {target_name} (rédigé à la 3ème personne, expliquant la valeur en 40 mots).

Format JSON STRICT :
{{
    "ask_to_connector": "Message à l'intermédiaire",
    "forwardable_blurb": "Paragraphe prêt à transférer"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "ask_to_connector": f"Hello {mutual_contact_name}, j'ai vu que tu étais connecté avec {target_name} chez {target_company}. Serais-tu à l'aise pour nous mettre en relation ? Je t'ai préparé un court texte transférable ci-dessous pour ne pas te faire perdre de temps.",
                "forwardable_blurb": f"Hello {target_name},\n\nJe te partage le profil de notre équipe qui aide les entreprises comme {target_company} à automatiser leur prospection et générer +35% de rendez-vous qualifiés.\n\nSeriez-vous ouverts à échanger 5 minutes ?"
            }

warm_intro_engine = WarmIntroEngine()
