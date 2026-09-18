"""
MOTEUR DE DÉLOGEMENT DE CONCURRENTS (COMPETITOR DISPLACEMENT MATRIX)
Génère un angle d'attaque chirurgical basé sur les faiblesses du concurrent actuel du prospect
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

COMPETITOR_DATABASE = {
    "Lemlist / Waalaxy": "Manque d'intelligence conversationnelle dynamique, templates répétitifs, risque de ban élevé.",
    "Apollo.io / ZoomInfo": "Données souvent obsolètes en Europe, emails génériques non personnalisés, support distant.",
    "HubSpot / Salesforce": "Outils très lourds, coûteux par utilisateur, nécessitent des semaines de configuration manuelle.",
    "Prospection Manuelle / SDRs internes": "Coût humain élevé (3 500€/mois/rep), lenteur, burnout commercial, données non standardisées."
}

class CompetitorDisplacement:
    """Crée un pitch de transition fluide et non-agressif pour déloger un concurrent"""

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
                logger.error(f"Erreur init Displacement: {e}")

    def generate_switch_pitch(self, prospect: Dict[str, Any], current_competitor: str, our_solution: str) -> Dict[str, Any]:
        """Génère une stratégie de bascule élégante et percutante"""
        comp_flaws = COMPETITOR_DATABASE.get(current_competitor, "Manque de flexibilité et d'intelligence prédictive")

        if not self.model:
            return {
                "competitor": current_competitor,
                "wedge_angle": f"Complémentarité et dépassement des limites de {current_competitor}",
                "displacement_email": f"Bonjour,\n\nBeaucoup d'utilisateurs de {current_competitor} nous rejoignent pour éliminer les tâches manuelles.\n\nSeriez-vous ouvert à une comparaison en 2 min ?"
            }

        prompt = f"""
Tu es un stratège commercial expert en 'Competitor Displacement' (conquête de clients chez la concurrence).

PROSPECT : {prospect.get('first_name')} ({prospect.get('position')} chez {prospect.get('company')})
OUTIL / SOLUTION QU'ILS UTILISENT DÉJÀ : {current_competitor}
FAIBLESSES CONNUES DE CE CONCURRENT : {comp_flaws}
NOTRE SOLUTION : {our_solution}

RÈGLES STRICTES :
1. Ne JAMAIS dénigrer vulgairement le concurrent (cela braque le prospect qui a choisi cet outil).
2. Valider d'abord la qualité de leur outil actuel.
3. Poser une question percutante sur le goulet d'étranglement bien connu que leur outil actuel ne sait pas résoudre.
4. Proposer une comparaison sans engagement.

Format STRICT JSON :
{{
    "competitor_targeted": "{current_competitor}",
    "wedge_strategy": "L'angle de faille exploité",
    "subject": "Objet d'email percutant",
    "displacement_body": "Corps de l'email court (< 70 mots)",
    "killer_question": "La question qui fait douter de son outil actuel"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "competitor_targeted": current_competitor,
                "wedge_strategy": "Augmentation de la valeur",
                "subject": f"Au-delà de {current_competitor} pour {prospect.get('company')}",
                "displacement_body": f"Bonjour {prospect.get('first_name')},\n\n{current_competitor} est une excellente base. Mais la plupart des équipes commerciales plafonnent sur la personnalisation réelle.\n\nNotre moteur IA s'interface avec vos flux pour générer +40% de réponses.\n\nCurieux de voir la différence ?",
                "killer_question": f"Quel est votre taux de réponse moyen actuel avec {current_competitor} ?"
            }

competitor_displacement = CompetitorDisplacement()
