"""
DÉTECTEUR DE GHOSTING ET RELANCES DE RUPTURE (GHOSTING BUSTER MATRIX)
Réactive les prospects silencieux après une démo, un devis ou une proposition
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

class GhostingBuster:
    """Génère des relances de rupture psychologique pour débloquer les deals silencieux"""

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
                logger.error(f"Erreur init GhostingBuster: {e}")

    def generate_reactivation_tactics(self, prospect_name: str, company: str, last_interaction_topic: str = "Envoi de la proposition tarifaire") -> Dict[str, Any]:
        """Génère 3 angles de relance anti-silence"""
        if not self.model:
            return {
                "nine_word_email": f"Bonjour {prospect_name}, êtes-vous toujours intéressé par l'optimisation commerciale de {company} ?",
                "guilt_free_breakup": f"Bonjour {prospect_name},\n\nSans retour de votre part, je suppose que vos priorités ont changé pour {company}, ce qui est tout à fait normal. Je clôture votre dossier pour ne pas encombrer votre boîte mail.\n\nBien à vous,",
                "zero_pressure_value": f"Bonjour {prospect_name},\n\nJ'ai pensé à vous en découvrant cette étude de cas récente sur votre secteur. Aucun besoin de me répondre, je voulais simplement vous la partager !\n\nBien à vous,"
            }

        prompt = f"""
Tu es un maître mondial du Closing B2B et de la négociation de crise.
Prospect : {prospect_name} chez {company}.
Dernier sujet abordé : "{last_interaction_topic}".
Statut : Le prospect ne répond plus depuis plus de 10 jours (Ghosting).

TÂCHE :
Rédige 3 variantes de réactivation psychologique à fort impact :
1. "nine_word_email" : L'email ultra-court en 1 seule phrase interrogative (Framework Dean Jackson, max 12 mots).
2. "guilt_free_breakup" : L'email d'abandon bienveillant qui libère le prospect de la pression et déclenche souvent la réponse de culpabilité positive.
3. "zero_pressure_value" : Un apport de valeur pur sans aucune relance de vente, désamorçant la méfiance.

Format JSON STRICT :
{{
    "nine_word_email": "texte",
    "guilt_free_breakup": "texte",
    "zero_pressure_value": "texte"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "nine_word_email": f"Bonjour {prospect_name}, êtes-vous toujours focalisé sur la prospection chez {company} ?",
                "guilt_free_breakup": f"Bonjour {prospect_name},\n\nJe n'ai pas eu de retour à mes messages précédents. Je conclus que le timing n'est plus opportun et je classe votre dossier.\n\nBonne continuation,",
                "zero_pressure_value": f"Bonjour {prospect_name},\n\nVoici un aperçu de nos derniers benchmarks SaaS. J'espère que cela sera utile à vos équipes !\n\nBien à vous,"
            }

ghosting_buster = GhostingBuster()
