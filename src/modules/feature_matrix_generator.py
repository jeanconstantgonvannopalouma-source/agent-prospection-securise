"""
GÉNÉRATEUR DE MATRICE COMPARATIVE SUR-MESURE
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

VALID_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest"
]

class FeatureMatrixGenerator:
    """Génère des comparatifs clairs et épurés entre notre offre et les alternatives"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def generate_comparison_matrix(self, competitor_or_method: str, prospect_company: str) -> Dict[str, Any]:
        our_name = "Jean Constant"

        if not self.api_key:
            return {
                "competitor": competitor_or_method,
                "comparison_text": f"COMPARATIF : SOLUTION JEAN CONSTANT vs {competitor_or_method.upper()}\n\n1. Personnalisation IA : Automatique vs Manuelle\n2. Gain de temps : +15h/semaine vs Faible\n3. Garantie : Résultats sous 14j vs Aucune",
                "key_takeaway": "Un passage à l'automatisation IA permet de diviser le coût d'acquisition par deux."
            }

        try:
            genai.configure(api_key=self.api_key)
            prompt = f"""
Tu es l'agent de prospection personnalisé de Jean Constant.
AIDE À VENDRE : Solution de prospection IA de Jean Constant.
ALTERNATIVE / CONCURRENT DU CLIENT : {competitor_or_method}
ENTREPRISE PROSPECTÉE : {prospect_company}

TÂCHE :
Génère une comparaison synthétique et percutante montrant pourquoi la solution de Jean Constant est plus efficace que {competitor_or_method}.

RÈGLES STRICTES DE FORMATAGE (ZERO PARASITE) :
- N'utilise AUCUN astérisque (* ou **), AUCUNE ligne de séparation (*** ou ---), AUCUNE italique.
- Présente la comparaison de manière aérée et nette.

Format JSON STRICT :
{{
    "competitor": "{competitor_or_method}",
    "comparison_text": "Texte comparatif propre et structuré",
    "key_takeaway": "Enseignement clé en 1 phrase"
}}
"""
            for model_name in VALID_MODELS:
                try:
                    m = genai.GenerativeModel(model_name)
                    resp = m.generate_content(prompt)
                    clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
                    data = json.loads(clean)
                    data["comparison_text"] = data.get("comparison_text", "").replace("***", "").replace("---", "=")
                    return data
                except Exception:
                    continue
        except Exception:
            pass

        return {
            "competitor": competitor_or_method,
            "comparison_text": f"Comparatif {our_name} vs {competitor_or_method} : Automatisation complète et gain de 15h par semaine.",
            "key_takeaway": "L'automatisation IA apporte une vitesse d'exécution inégalée."
        }

feature_matrix_generator = FeatureMatrixGenerator()
