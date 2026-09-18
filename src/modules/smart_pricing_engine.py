"""
MOTEUR DE TARIFICATION DYNAMIQUE & SIMULATEUR DE REMISES (TIERED PRICING ENGINE)
"""
from typing import Dict, Any

class SmartPricingEngine:
    """Calcule des propositions tarifaires à 3 paliers et simule les remises annuelles"""

    def generate_tier_pricing(self, sales_team_size: int = 5, base_price_per_user_monthly: float = 290.0) -> Dict[str, Any]:
        """Génère 3 forfaits personnalisés avec calcul de ROI"""
        starter_users = max(1, int(sales_team_size * 0.4))
        growth_users = sales_team_size
        scale_users = int(sales_team_size * 1.5)

        # Calculs Forfait Starter
        starter_monthly = starter_users * base_price_per_user_monthly
        starter_annual = starter_monthly * 12 * 0.85 # -15% remise annuelle

        # Calculs Forfait Growth (Recommandé)
        growth_monthly = growth_users * (base_price_per_user_monthly * 0.90) # -10% volume
        growth_annual = growth_monthly * 12 * 0.80 # -20% remise annuelle

        # Calculs Forfait Scale / Enterprise
        scale_monthly = scale_users * (base_price_per_user_monthly * 0.80) # -20% volume
        scale_annual = scale_monthly * 12 * 0.75 # -25% remise annuelle

        return {
            "team_size": sales_team_size,
            "tiers": {
                "Starter (Pilote 1 Équipe)": {
                    "users": starter_users,
                    "monthly_price_eur": round(starter_monthly),
                    "annual_price_eur": round(starter_annual),
                    "annual_savings_eur": round((starter_monthly * 12) - starter_annual),
                    "scope": "1 Canal (Email) + 500 prospects enrichis/mois"
                },
                "Growth (Équipe Complète - Recommandé)": {
                    "users": growth_users,
                    "monthly_price_eur": round(growth_monthly),
                    "annual_price_eur": round(growth_annual),
                    "annual_savings_eur": round((growth_monthly * 12) - growth_annual),
                    "scope": "Multi-Canal (Email + LinkedIn) + Accès API + Intégration CRM"
                },
                "Scale / Enterprise (Pleine Puissance)": {
                    "users": scale_users,
                    "monthly_price_eur": round(scale_monthly),
                    "annual_price_eur": round(scale_annual),
                    "annual_savings_eur": round((scale_monthly * 12) - scale_annual),
                    "scope": "Tout inclus + Démon 24/7 + Radar Signaux Live + Account Manager Dédié"
                }
            }
        }

smart_pricing_engine = SmartPricingEngine()
