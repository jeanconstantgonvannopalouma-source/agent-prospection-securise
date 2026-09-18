"""
MATRICE DE FUSION DES SIGNAUX & BUYING INTENT HEATMAP
Fusionne les signaux (News + Hiring + Tech + Funding) pour calculer l'urgence d'achat
"""
import os
import re
import json
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

class IntentHeatMatrix:
    """Calcule la température d'achat globale et le canal prioritaire"""

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
                logger.error(f"Erreur init IntentHeatMatrix: {e}")

    def compute_intent_heatmap(
        self,
        company_name: str,
        hiring_signal: str = "",
        funding_signal: str = "",
        news_signal: str = "",
        tech_stack: List[str] = None
    ) -> Dict[str, Any]:
        """Fusionne les signaux et génère la recommandation stratégique"""
        tech_list = tech_stack or ["Stack SaaS Standard"]
        
        # Calcul de base déterministe
        heat_score = 40
        reasons = []

        if hiring_signal and len(hiring_signal) > 5:
            heat_score += 20
            reasons.append("Recrutements actifs en cours (+20 pts)")
        if funding_signal and len(funding_signal) > 5:
            heat_score += 25
            reasons.append("Levée de fonds / Capital disponible (+25 pts)")
        if news_signal and len(news_signal) > 5:
            heat_score += 15
            reasons.append("Actualité économique brûlante (+15 pts)")
        if len(tech_list) >= 2:
            heat_score += 10
            reasons.append("Stack digitale mature (+10 pts)")

        final_score = min(100, heat_score)
        
        if final_score >= 80:
            urgency_status = "🔥 BRÛLANT (Contacter sous 24h)"
            recommended_channel = "Multi-Canal Agressif (Email + LinkedIn + Téléphone)"
        elif final_score >= 60:
            urgency_status = "🟡 TIÈDE / OPPORTUNITÉ FORTE"
            recommended_channel = "Cold Email PAS + Invitation LinkedIn"
        else:
            urgency_status = "⚪ STANDARD (Nurturing)"
            recommended_channel = "Cold Email Éducatif (Preuve Sociale)"

        if not self.model:
            return {
                "company": company_name,
                "intent_heat_score": final_score,
                "urgency_status": urgency_status,
                "recommended_channel": recommended_channel,
                "signal_breakdown": reasons,
                "actionable_insight": f"Priorité {urgency_status} pour {company_name}."
            }

        prompt = f"""
Tu es un Directeur des Opérations de Revenus (VP RevOps).
Entreprise : {company_name}
Signaux détectés :
- Recrutement : {hiring_signal or 'Aucun'}
- Financement : {funding_signal or 'Aucun'}
- Actualités : {news_signal or 'Aucun'}
- Stack Tech : {', '.join(tech_list)}
Score calculé : {final_score}/100

TÂCHE :
Rédige en 2 phrases concises la synthèse de timing commercial : Pourquoi est-ce LE moment idéal pour leur vendre maintenant ?

Format JSON STRICT :
{{
    "intent_heat_score": {final_score},
    "urgency_status": "{urgency_status}",
    "recommended_channel": "{recommended_channel}",
    "signal_breakdown": {json.dumps(reasons, ensure_ascii=False)},
    "executive_timing_rationale": "Pourquoi acheter maintenant et pas dans 6 mois"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "intent_heat_score": final_score,
                "urgency_status": urgency_status,
                "recommended_channel": recommended_channel,
                "signal_breakdown": reasons,
                "executive_timing_rationale": f"La convergence des signaux récents rend le timing d'approche particulièrement favorable chez {company_name}."
            }

intent_heat_matrix = IntentHeatMatrix()
