"""
CALCULATEUR DE PERTE FINANCIÈRE ET ROI DYNAMIQUE (LOSS & ROI ENGINE)
"""
from typing import Dict, Any

class DynamicROICalculator:
    """Calcule le coût de l'inaction et le retour sur investissement d'une prospection par IA"""

    def compute_inaction_cost(self, sales_team_size: int = 5, sdr_monthly_salary: float = 3800.0) -> Dict[str, Any]:
        """
        Calcule les heures perdues sur des tâches de prospection manuelles et le coût financier associé
        """
        # Un commercial passe en moyenne 35% de son temps à chercher/enrichir/rédiger manuellement des mails
        hours_per_week_lost_per_rep = 14.0
        monthly_hours_lost_per_rep = hours_per_week_lost_per_rep * 4.2
        hourly_rep_cost = sdr_monthly_salary / 151.67 # Coût horaire moyen
        
        monthly_waste_per_rep = monthly_hours_lost_per_rep * hourly_rep_cost
        total_monthly_waste = monthly_waste_per_rep * sales_team_size
        annual_financial_waste = total_monthly_waste * 12

        # Gain d'opportunités récupérées
        extra_meetings_per_rep_month = 6
        total_extra_meetings_month = extra_meetings_per_rep_month * sales_team_size

        return {
            "sales_team_size": sales_team_size,
            "hours_lost_per_week_team": int(hours_per_week_lost_per_rep * sales_team_size),
            "monthly_financial_waste_eur": round(total_monthly_waste, 2),
            "annual_financial_waste_eur": round(annual_financial_waste, 2),
            "extra_meetings_unlocked_month": total_extra_meetings_month,
            "loss_snippet": f"Votre équipe de {sales_team_size} commerciaux perd ~{round(total_monthly_waste):,} € chaque mois en temps de saisie manuelle.",
            "roi_snippet": f"Débloquez +{total_extra_meetings_month} démos qualifiées par mois dès le premier cycle de 30 jours."
        }

roi_calculator = DynamicROICalculator()
