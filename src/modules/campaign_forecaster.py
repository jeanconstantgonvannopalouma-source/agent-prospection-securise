"""
SIMULATEUR PRÉDICTIF DE REVENUS ET DE PERFORMANCE DE CAMPAGNE (FORECASTER)
"""
from typing import Dict, Any

class CampaignForecaster:
    """Calcule les projections de conversion et de ROI d'une campagne B2B"""

    def forecast_campaign(
        self,
        lead_count: int = 100,
        average_deal_value: float = 3500.0,
        target_industry: str = "Tech / B2B",
        deliverability_score: int = 95
    ) -> Dict[str, Any]:
        """Simulation statistique de l'entonnoir de prospection"""
        
        # Coefficients réalistes basés sur les standards de l'industrie (Cold Email B2B optimisé IA)
        open_rate = (deliverability_score / 100.0) * 0.65  # ~62% d'ouverture
        reply_rate = 0.12  # ~12% de taux de réponse global
        positive_reply_share = 0.40  # 40% des réponses sont positives / ouvertes à un échange
        meeting_booking_rate = 0.65  # 65% des leads positifs se transforment en RDV démo
        closing_rate = 0.25  # 25% des démos signent un contrat

        # Calcul des volumes projetés
        emails_opened = int(lead_count * open_rate)
        replies_received = int(emails_opened * reply_rate)
        positive_leads = int(replies_received * positive_reply_share)
        meetings_booked = max(1, int(positive_leads * meeting_booking_rate)) if lead_count >= 10 else 1
        deals_closed = max(1, int(meetings_booked * closing_rate)) if meetings_booked >= 4 else 1

        projected_revenue = deals_closed * average_deal_value
        estimated_time_hours_saved = round(lead_count * 0.25, 1) # 15 min économisées par prospect vs prospection manuelle

        return {
            "lead_count": lead_count,
            "deliverability_factor": f"{deliverability_score}%",
            "estimated_opens": emails_opened,
            "estimated_replies": replies_received,
            "qualified_hot_leads": positive_leads,
            "projected_meetings": meetings_booked,
            "projected_deals": deals_closed,
            "projected_pipeline_val_eur": round(meetings_booked * average_deal_value, 2),
            "projected_signed_revenue_eur": round(projected_revenue, 2),
            "hours_saved_by_ai": estimated_time_hours_saved
        }

campaign_forecaster = CampaignForecaster()
