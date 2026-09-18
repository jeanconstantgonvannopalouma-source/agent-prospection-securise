"""
MOTEUR DE DÉCLENCHEURS WORKFLOW AUTOMATISÉS (TRIGGER ENGINE)
"""
from typing import Dict, Any, List

class TriggerWorkflowEngine:
    """Évalue le comportement d'un prospect et déclenche l'action suivante"""

    def evaluate_next_best_action(self, event_type: str, prospect_name: str, company: str) -> Dict[str, Any]:
        rules = {
            "EMAIL_OPENED_TWICE": {
                "action": "Envoyer une note d'invitation LinkedIn",
                "timing": "Immédiat (sous 2 heures)",
                "reason": "Intérêt élevé détecté par la double ouverture"
            },
            "NO_REPLY_5_DAYS": {
                "action": "Déclencher la Relance Bump Doux",
                "timing": "J+5 ouvrés",
                "reason": "Rappel courtois non-intrusif"
            },
            "OBJECTION_PRICING": {
                "action": "Envoyer le Calculateur de ROI et le comparatif",
                "timing": "Immédiat",
                "reason": "Désamorcer le doute sur le prix par le coût d'inaction"
            },
            "POSITIVE_REPLY": {
                "action": "Transmettre le lien de réservation Calendly et le One-Pager",
                "timing": "Immédiat (sous 15 minutes)",
                "reason": "Maximiser le taux de conversion sur lead chaud"
            }
        }

        matched = rules.get(event_type, {
            "action": "Maintenir la cadence standard",
            "timing": "J+3",
            "reason": "Suivi classique de campagne"
        })

        return {
            "event": event_type,
            "prospect": f"{prospect_name} ({company})",
            "recommended_next_action": matched["action"],
            "execution_timing": matched["timing"],
            "strategy_reason": matched["reason"]
        }

trigger_engine = TriggerWorkflowEngine()
