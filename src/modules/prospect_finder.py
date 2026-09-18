"""
MOTEUR DE RECHERCHE, ENRICHISSEMENT ET SCORING STRATOSPHÉRIQUE
"""
import logging
import json
import re
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()
logger = logging.getLogger(__name__)

class StratosphericProspectFinder:
    """Recherche, qualification et enrichissement intelligent de prospects"""

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
                logger.error(f"Erreur init Gemini Finder: {e}")

    def validate_email_syntax(self, email: str) -> bool:
        """Vérifie la syntaxe d'un email de manière stricte"""
        if not email or not isinstance(email, str):
            return False
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email.strip()))

    def calculate_icp_score(self, prospect_data: Dict[str, Any]) -> int:
        """
        Calcule un score déterministe d'adéquation au profil idéal (ICP Fit Score /100)
        """
        score = 40  # Base
        role = (prospect_data.get('position') or prospect_data.get('job_title') or '').lower()
        company = (prospect_data.get('company') or prospect_data.get('company_name') or '').lower()
        industry = (prospect_data.get('industry') or '').lower()

        # Décideurs de haut niveau (+30 pts)
        if any(w in role for w in ['ceo', 'fondateur', 'founder', 'directeur', 'vp', 'head of', 'dirigeant']):
            score += 30
        elif any(w in role for w in ['manager', 'lead', 'responsable']):
            score += 15

        # Secteurs à haute valeur (+20 pts)
        if any(w in industry for w in ['tech', 'saas', 'software', 'ia', 'ai', 'b2b', 'conseil', 'digital']):
            score += 20

        # Signaux d'intention connus (+10 pts)
        if prospect_data.get('notes') or prospect_data.get('intent_signal'):
            score += 10

        return min(100, max(0, score))

    def enrich_with_ai(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Utilise Gemini pour déduire les défis probables et l'angle d'attaque
        """
        enriched = prospect_data.copy()
        
        # Validation email
        enriched['is_valid_email'] = self.validate_email_syntax(enriched.get('email', ''))
        
        # Calcul du score ICP
        enriched['qualification_score'] = self.calculate_icp_score(enriched)
        enriched['conversion_probability'] = round(enriched['qualification_score'] / 100.0, 2)

        # Si l'IA est disponible, on extrait un signal d'intention stratégique
        if self.model:
            try:
                prompt = f"""
Prospect :
- Entreprise: {enriched.get('company', '')}
- Rôle: {enriched.get('position', '')}
- Secteur: {enriched.get('industry', '')}
- Contexte additionnel: {enriched.get('notes', 'Aucun')}

En 1 phrase courte, identifie le défi commercial #1 que cette personne affronte en ce moment.
Réponds au format JSON : {{"top_pain_point": "Le défi identifié", "recommended_angle": "L'angle de vente conseillé"}}
"""
                resp = self.model.generate_content(prompt)
                clean_txt = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE)
                data = json.loads(clean_txt)
                enriched['top_pain_point'] = data.get('top_pain_point', '')
                enriched['recommended_angle'] = data.get('recommended_angle', '')
            except Exception:
                enriched['top_pain_point'] = "Acquisition de nouveaux clients qualifiés"
                enriched['recommended_angle'] = "Automatisation & Gain de temps"
        else:
            enriched['top_pain_point'] = "Génération de leads"
            enriched['recommended_angle'] = "Augmentation du ROI"

        return enriched

prospect_finder = StratosphericProspectFinder()
