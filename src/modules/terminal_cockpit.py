"""
COCKPIT DE MONITORING LIVE DU SYSTÈME STRATOSPHÉRIQUE
"""
import os
import sys
from modules.pipeline_tracker import pipeline_tracker
from modules.warmup_engine import warmup_engine
from modules.message_engine import message_engine
from modules.autopilot_daemon import autopilot_daemon

class TerminalCockpit:
    """Affiche le centre de commandement en temps réel"""

    def render(self):
        stats = pipeline_tracker.get_stats()
        safe_limit = warmup_engine.get_daily_safe_limit()
        model_name = message_engine.active_model_name or "Gemini 3.7 / 3.6 Flash"
        daemon_status = "🟢 ACTIF (En veille)" if autopilot_daemon.is_running else "⚪ EN PAUSE"

        cockpit_view = f"""
===================================================================================
                    🛰️  CENTRE DE COMMANDEMENT QUANTIQUE V8.0
===================================================================================
 [SYSTÈME]
  • Moteur IA Actif      : {model_name}
  • Démon Autonome       : {daemon_status}
  • Limite Sécurisée/Jour: {safe_limit} emails max / jour (Anti-Ban Warmup)
  • Prospects Traités    : {autopilot_daemon.processed_count} en tâche de fond

 [PIPELINE COMMERCIAL & RÉSULTATS]
  • Total Prospects Base : {stats['total_prospects']}
  • Contacts Effectués   : {stats['contacted_count']}
  • Deals Gagnés         : {stats['deals_won']}
  • VALEUR PIPELINE (€)  : {stats['total_pipeline_value_eur']:,.2f} €

 [DERNIÈRES ACTIVITÉS CRM]"""
        
        print(cockpit_view)
        if stats["recent_prospects"]:
            for idx, p in enumerate(stats["recent_prospects"][:4], 1):
                print(f"  [{idx}] {p['first_name']} chez {p['company']} ({p['position']}) ➔ Statut: {p['status']} | Deal: {p['estimated_deal_value']} €")
        else:
            print("  Aucune activité récente enregistrée.")
            
        print("===================================================================================")

terminal_cockpit = TerminalCockpit()
