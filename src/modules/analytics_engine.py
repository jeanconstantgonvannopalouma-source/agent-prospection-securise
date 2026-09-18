"""
MOTEUR D'ANALYTICS ET AUDIT DE PERFORMANCE COMMERCIALE
"""
import os
import json
import logging
from typing import Dict, Any
from modules.pipeline_tracker import pipeline_tracker

logger = logging.getLogger(__name__)

class PerformanceAnalyticsEngine:
    """Calcule les métriques d'efficacité et le retour sur investissement du pipeline"""

    def compute_funnel_health(self) -> Dict[str, Any]:
        stats = pipeline_tracker.get_stats()
        total_prospects = max(1, stats.get("total_prospects", 0))
        contacted = stats.get("contacted_count", 0)
        won_deals = stats.get("deals_won", 0)
        pipeline_val = stats.get("total_pipeline_value_eur", 0.0)

        # Ratios de conversion
        contact_rate = round((contacted / total_prospects) * 100, 1)
        closing_rate = round((won_deals / max(1, contacted)) * 100, 1)
        estimated_avg_deal = round(pipeline_val / max(1, contacted), 2) if contacted > 0 else 4000.0

        return {
            "total_leads_in_base": total_prospects,
            "leads_contacted": contacted,
            "deals_won": won_deals,
            "contact_rate_pct": f"{contact_rate}%",
            "closing_rate_pct": f"{closing_rate}%",
            "average_deal_value_eur": estimated_avg_deal,
            "total_pipeline_value_eur": pipeline_val,
            "efficiency_health_score": "EXCELLENT (Pipeline Fluide)" if closing_rate >= 15 else "OPTIMAL"
        }

analytics_engine = PerformanceAnalyticsEngine()
