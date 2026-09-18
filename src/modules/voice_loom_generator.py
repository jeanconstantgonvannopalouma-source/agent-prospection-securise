"""
GÉNÉRATEUR DE SCRIPTS POUR MESSAGES VOCAUX LINKEDIN ET VIDÉOS LOOM (60 SECONDES)
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

class VoiceLoomGenerator:
    """Rédige des scripts ultra-engageants pour notes vocales et capsules vidéos Loom"""

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
                logger.error(f"Erreur init VoiceLoom: {e}")

    def generate_voice_and_loom_script(self, prospect: Dict[str, Any], value_prop: str) -> Dict[str, Any]:
        """Génère le script vocal LinkedIn (< 45s) et le script vidéo Loom (60s)"""
        p_name = prospect.get("first_name", "Thomas")
        p_company = prospect.get("company", "l'Entreprise")
        p_role = prospect.get("position", "Directeur")
        p_notes = prospect.get("notes", "Expansion commerciale")

        if not self.model:
            return {
                "linkedin_voice_note_script": f"Hello {p_name}, j'espère que tu vas bien. Je regardais vos projets chez {p_company}. On aide les équipes comme la tienne à générer +40% de RDVs. Dis-moi si tu es ouvert à un micro échange !",
                "loom_video_script": {
                    "hook_0_10s": f"Montrer leur site web : 'Hello {p_name}, je regardais votre positionnement chez {p_company}...'",
                    "core_value_10_40s": "Montrer notre plateforme en action : 'Voici comment générer des leads qualifiés sans effort manuel.'",
                    "cta_close_40_60s": "'Dis-moi si ça fait écho à tes priorités ce trimestre !'"
                }
            }

        prompt = f"""
Tu es un maître de la prospection multi-format moderne (LinkedIn Audio Notes & Vidéos Loom 1-to-1).

PROSPECT : {p_name} ({p_role} chez {p_company})
SIGNAL : {p_notes}
SOLUTION : {value_prop}

TÂCHE :
1. "linkedin_voice_note_script" : Texte exact d'une note vocale LinkedIn naturelle, chaleureuse et sans récitation (30 à 45 secondes de parole max, ~60-80 mots).
2. "loom_video_script" : Découpage chronologique d'une vidéo personnalisée de 60 secondes chrono (avec instructions d'écran).

Format STRICT JSON :
{{
    "linkedin_voice_note_script": "Texte complet à prononcer au micro",
    "voice_tone_advice": "Conseil d'intonation pour maximiser la confiance",
    "loom_video_script": {{
        "step_1_hook_0_15s": "Action visuelle + Parole d'accroche",
        "step_2_demo_15_45s": "Ce qu'on montre à l'écran + Explication de la valeur",
        "step_3_cta_45_60s": "Clôture souple et sans pression"
    }}
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "linkedin_voice_note_script": f"Hello {p_name} ! Je te laisse un rapide vocal car je suivais vos actualités chez {p_company}. On aide les {p_role}s à automatiser leur prospection sortante. Fais-moi signe si tu es partant pour un rapide échange !",
                "voice_tone_advice": "Souriant, calme, ton entre pairs",
                "loom_video_script": {
                    "step_1_hook_0_15s": f"Afficher la page LinkedIn de {p_company} en arrière-plan",
                    "step_2_demo_15_45s": "Montrer l'interface de notre solution IA en 2 clics",
                    "step_3_cta_45_60s": "Proposer de transmettre une version d'essai"
                }
            }

voice_loom_generator = VoiceLoomGenerator()
