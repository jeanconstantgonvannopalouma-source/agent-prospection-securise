"""
MOTEUR D'AUTO-APPRENTISSAGE ET D'ÉVOLUTION CONTINUE DES PROMPTS (AUTO-EVOLVER)
"""
import os
import re
import json
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai
from modules.pipeline_tracker import pipeline_tracker

load_dotenv()
logger = logging.getLogger(__name__)

RULES_FILE = os.path.join("data", "evolution_rules.json")

class PromptAutoEvolver:
    """Analyse les performances passées et crée de nouvelles règles d'écriture pour l'IA"""

    def __init__(self):
        os.makedirs("data", exist_ok=True)
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
                logger.error(f"Erreur init Evolver: {e}")

    def load_learned_rules(self) -> List[str]:
        """Charge les règles issues des apprentissages précédents"""
        if os.path.exists(RULES_FILE):
            try:
                with open(RULES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return [
            "Toujours formuler l'appel à l'action sous forme d'une question fermée à faible engagement.",
            "Ne jamais dépasser 3 phrases pour le corps principal du message.",
            "Bannir les formules de politesse introductives creuses ('J'espère que vous allez bien')."
        ]

    def trigger_self_learning_cycle(self) -> Dict[str, Any]:
        """Génère de nouvelles règles d'optimisation basées sur l'intelligence collective"""
        current_rules = self.load_learned_rules()
        stats = pipeline_tracker.get_stats()

        if not self.model:
            return {"status": "ok", "new_rules": current_rules, "learning_insights": "Règles standard maintenues."}

        prompt = f"""
Tu es un Directeur Scientifique du Copywriting IA.
RÈGLES D'ÉCRITURE ACTUELLES :
{json.dumps(current_rules, ensure_ascii=False)}

STATISTIQUES ACTUELLES :
{json.dumps(stats, ensure_ascii=False)}

TÂCHE :
Génère 1 nouvelle règle d'écriture ultra-pointue (maximisant le taux de réponse sans paraître agressif) pour enrichir notre base de connaissances.

Format STRICT JSON :
{{
    "new_rule": "Règle concrète à appliquer dans tous les futurs emails",
    "rationale": "Pourquoi cette règle améliore la conversion psychologique"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            data = json.loads(clean)
            
            new_rule = data.get("new_rule")
            if new_rule and new_rule not in current_rules:
                current_rules.append(new_rule)
                with open(RULES_FILE, "w", encoding="utf-8") as f:
                    json.dump(current_rules, f, ensure_ascii=False, indent=2)

            return {
                "status": "success",
                "total_active_rules": len(current_rules),
                "latest_rule_added": new_rule,
                "rationale": data.get("rationale")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

prompt_evolver = PromptAutoEvolver()
