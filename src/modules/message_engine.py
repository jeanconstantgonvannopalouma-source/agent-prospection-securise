"""
MOTEUR DE COPYWRITING MULTI-CANAL AVEC BASE DE CONNAISSANCES DE JEAN CONSTANT
"""
import os
import json
import logging
import re
from typing import Dict, Optional, Any
from dotenv import load_dotenv
import google.generativeai as genai
from modules.knowledge_base import knowledge_base

load_dotenv()
logger = logging.getLogger(__name__)

VALID_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash"
]

class StratosphericMessageEngine:
    """Moteur IA exploitant la base de connaissances métier de Jean Constant"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.active_model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Erreur init Gemini: {e}")

    def _call_gemini_resilient(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None

        full_prompt = f"{prompt}\n\nIMPORTANT: Réponds STRICTEMENT au format JSON valide, sans Markdown ```json autour."

        for model_name in VALID_MODELS:
            if not model_name: continue
            try:
                m = genai.GenerativeModel(model_name)
                response = m.generate_content(full_prompt)
                self.active_model_name = model_name
                return response.text.strip()
            except Exception:
                continue

        return None

    def _call_gemini_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        raw_text = self._call_gemini_resilient(prompt)
        if not raw_text:
            return None
        try:
            text = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
            text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE).strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Erreur parsing JSON: {e}")
            return None

    def generate_ab_test_messages(self, prospect: Any, value_prop: str = "") -> Dict[str, Any]:
        p_name = getattr(prospect, 'first_name', None) or (prospect.get('first_name') if isinstance(prospect, dict) else 'Bonjour')
        p_company = getattr(prospect, 'company_name', None) or (prospect.get('company') if isinstance(prospect, dict) else 'votre entreprise')
        p_role = getattr(prospect, 'job_title', None) or (prospect.get('position') if isinstance(prospect, dict) else 'Dirigeant')
        p_industry = getattr(prospect, 'industry', None) or (prospect.get('industry') if isinstance(prospect, dict) else 'B2B')
        p_notes = getattr(prospect, 'notes', None) or (prospect.get('notes') if isinstance(prospect, dict) else '')

        # Injection automatique de la base de connaissances
        kb_context = knowledge_base.get_prompt_context()

        prompt = f"""
{kb_context}

Rédige 2 variantes d'emails de prospection distinctes pour un A/B Test B2B.

PROSPECT : {p_name}, {p_role} chez {p_company} (Secteur : {p_industry}).
SIGNAL / ACTUALITÉ : {p_notes}
OFFRE À VENDRE : {value_prop or knowledge_base.kb_data.get('core_value_prop')}

Format JSON STRICT :
{{
    "variant_a": {{
        "subject": "objet A",
        "body": "corps email A",
        "angle": "Framework PAS (Douleur)"
    }},
    "variant_b": {{
        "subject": "objet B",
        "body": "corps email B",
        "angle": "Framework BAB (Preuve Sociale)"
    }}
}}
"""
        res = self._call_gemini_json(prompt)
        if not res:
            res = {
                "variant_a": {
                    "subject": f"Question rapide pour {p_company}",
                    "body": f"Bonjour {p_name},\n\nProspecter manuellement prend jusqu'à 15h par semaine. Nous aidons les {p_role}s à automatiser cela.\n\nSeriez-vous ouvert à un rapide échange de 2 min ?",
                    "angle": "Douleur"
                },
                "variant_b": {
                    "subject": f"Résultats pour {p_company}",
                    "body": f"Bonjour {p_name},\n\nNous avons aidé des entreprises du secteur {p_industry} à générer +35% de rendez-vous qualifiés.\n\nSeriez-vous curieux de découvrir comment ?",
                    "angle": "Résultats"
                }
            }
        return res

    def generate_personalized_message(self, prospect: Any, value_prop: str = "", framework: str = "PAS") -> Dict[str, Any]:
        ab = self.generate_ab_test_messages(prospect, value_prop)
        chosen = ab.get("variant_a") if framework == "PAS" else ab.get("variant_b")
        return {
            "subject": chosen.get("subject"),
            "body": chosen.get("body"),
            "hook_used": chosen.get("angle"),
            "quality_score": 9.5,
            "framework": framework
        }

    def analyze_message_quality(self, message: str, subject: str = "") -> Dict[str, Any]:
        spam_words = ['gratuit', '100%', 'urgent', 'offre', 'argent', 'promo', 'revenu', 'gagner', 'miracle']
        found_spam = [w for w in spam_words if w in message.lower() or w in subject.lower()]
        words = len(message.split())
        has_cta = bool(re.search(r'\?|\b(disponible|échange|discuter|découvrir)\b', message, re.I))

        score = 100 - (len(found_spam) * 15)
        if words > 100: score -= 20
        if words < 20: score -= 15
        if not has_cta: score -= 20

        return {
            'word_count': words,
            'spam_triggers_found': found_spam,
            'has_clear_cta': has_cta,
            'deliverability_score': max(0, min(100, score)),
            'is_optimal': len(found_spam) == 0 and 30 <= words <= 90 and has_cta
        }

message_engine = StratosphericMessageEngine()
