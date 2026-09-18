"""
BASE DE CONNAISSANCES OFFICIELE DE JEAN CONSTANT GONVANNO PALOUMA
"""
import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

KB_FILE = os.path.join("data", "knowledge_base.json")

DEFAULT_KB = {
    "company_name": "Jean Constant - IA & Growth B2B",
    "owner_name": "Jean Constant Gonvanno Palouma",
    "owner_email": "jeanconstantgonvannopalouma@gmail.com",
    "owner_phone": "+33 6 20 07 81 93",
    "offer_title": "Système d'Acquisition & Prospection Commerciale Autonome par IA",
    "core_value_prop": "Générer +35% à +50% de rendez-vous qualifiés mensuels pour les équipes commerciales B2B.",
    "proof_points_and_case_studies": "- +42% de démos réservées dès le 1er mois\n- Gains de 15h/semaine par commercial",
    "guarantee": "Premier pipeline de RDVs qualifiés livré sous 14 jours."
}

class KnowledgeBaseManager:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.kb_data = self.load_kb()

    def load_kb(self) -> Dict[str, Any]:
        if os.path.exists(KB_FILE):
            try:
                with open(KB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["owner_name"] = "Jean Constant Gonvanno Palouma"
                    data["owner_email"] = "jeanconstantgonvannopalouma@gmail.com"
                    data["owner_phone"] = "+33 6 20 07 81 93"
                    return data
            except Exception:
                pass
        self.save_kb(DEFAULT_KB)
        return DEFAULT_KB

    def save_kb(self, data: Dict[str, Any]) -> bool:
        data["owner_name"] = "Jean Constant Gonvanno Palouma"
        data["owner_email"] = "jeanconstantgonvannopalouma@gmail.com"
        data["owner_phone"] = "+33 6 20 07 81 93"
        try:
            with open(KB_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.kb_data = data
            return True
        except Exception:
            return False

    def get_prompt_context(self) -> str:
        return f"""
PROFIL DE JEAN CONSTANT :
- Nom complet : Jean Constant Gonvanno Palouma
- Adresse e-mail officielle : jeanconstantgonvannopalouma@gmail.com
- Téléphone professionnel : +33 6 20 07 81 93
- Solution : {self.kb_data.get('offer_title')}
- Value Prop : {self.kb_data.get('core_value_prop')}
"""

knowledge_base = KnowledgeBaseManager()
