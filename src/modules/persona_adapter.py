"""
ADAPTATEUR PSYCHOMÉTRIQUE MULTI-PERSONAS
Adapte le pitch selon le profil psychologique du décideur (CEO, CRO, CFO, CTO)
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

PERSONA_ARCHETYPES = {
    "CEO": {
        "focus": "Vision, Croissance stratégique, Valorisation, Leadership de marché",
        "triggers": "Prendre de l'avance sur les concurrents, Libérer du temps pour la stratégie",
        "tone": "Ultra-synthétique, axé sur l'impact macro-économique"
    },
    "CRO_SALES": {
        "focus": "Pipeline commercial, Taux de closing, Atteinte des quotas, Ramp-up des SDRs",
        "triggers": "Combler le manque de leads qualifiés, Réduire le cycle de vente",
        "tone": "Énergique, orienté chiffres d'affaires et vélocité"
    },
    "CFO_FINANCE": {
        "focus": "Contrôle des coûts, Réduction du CAC, ROI mesurable, Payback rapide",
        "triggers": "Éviter les dépenses superflues, Rentabiliser chaque euro investi",
        "tone": "Factuel, prudent, démonstration financière rigoureuse"
    },
    "CTO_TECH": {
        "focus": "Sécurité, Stabilité, Architecture propre, Simplicité d'intégration",
        "triggers": "Éviter la dette technique, Automatiser les tâches répétitives sans friction",
        "tone": "Précis, technique, sans jargon marketing bullshit"
    }
}

class PersonaAdapter:
    """Détecte le persona et formule les arguments sur-mesure"""

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
                logger.error(f"Erreur init Persona Adapter: {e}")

    def detect_persona_type(self, position: str) -> str:
        """Associe un titre de poste à un archétype psychologique"""
        pos = position.lower()
        if any(w in pos for w in ["ceo", "fondateur", "founder", "directeur général", "dg", "président"]):
            return "CEO"
        elif any(w in pos for w in ["cro", "sales", "commercial", "revenu", "growth", "business development"]):
            return "CRO_SALES"
        elif any(w in pos for w in ["cfo", "finance", "daf", "financier", "comptable", "achat"]):
            return "CFO_FINANCE"
        elif any(w in pos for w in ["cto", "tech", "technique", "développeur", "eng", "infrastructure", "it"]):
            return "CTO_TECH"
        return "CRO_SALES"

    def generate_persona_pitch(self, prospect: Dict[str, Any], raw_value_prop: str) -> Dict[str, Any]:
        """Génère un angle d'attaque psychologique calibré sur le poste"""
        persona_key = self.detect_persona_type(prospect.get("position", ""))
        archetype = PERSONA_ARCHETYPES[persona_key]

        if not self.model:
            return {
                "persona_type": persona_key,
                "psychological_trigger": archetype["triggers"],
                "customized_angle": raw_value_prop
            }

        prompt = f"""
Tu es un expert en psychologie de la vente B2B.
Cible : {prospect.get('first_name')} - {prospect.get('position')} chez {prospect.get('company')}.
Archétype détecté : {persona_key} (Focus: {archetype['focus']}).
Offre brute : {raw_value_prop}

TÂCHE :
Reformule l'accroche et l'argument clé pour résonner à 100% avec les priorités secrètes de ce rôle ({persona_key}).
Ton recommandé : {archetype['tone']}.

Format JSON STRICT :
{{
    "persona_type": "{persona_key}",
    "core_driver": "Le levier psychologique activé",
    "tailored_pitch_angle": "L'angle de valeur reformulé spécifiquement pour ce rôle",
    "suggested_metric": "Métrique ou KPI qui va captiver ce profil (ex: -20% CAC, +40% RDVs, etc.)"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "persona_type": persona_key,
                "core_driver": archetype["focus"],
                "tailored_pitch_angle": raw_value_prop,
                "suggested_metric": "ROI immédiat"
            }

persona_adapter = PersonaAdapter()
