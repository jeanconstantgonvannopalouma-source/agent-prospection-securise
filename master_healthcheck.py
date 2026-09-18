"""
BANC D'ESSAI & AUTO-DIAGNOSTIC COMPLET DU SYSTÈME STRATOSPHÉRIQUE V10.0
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath("src"))

def run_healthcheck():
    print("\n" + "="*75)
    print("      🧪 AUDIT GÉNÉRAL DE SANTÉ DU SYSTÈME STRATOSPHÉRIQUE V10.0")
    print("="*75)

    modules_to_test = [
        ("Cerveau Copywriting Gemini", "modules.message_engine", "message_engine"),
        ("Recherche & Qualification", "modules.prospect_finder", "prospect_finder"),
        ("Moteur d'Envoi & Simulateur", "modules.email_sender", "email_sender"),
        ("Gestionnaire d'Objections", "modules.objection_handler", "objection_handler"),
        ("Traitement par Lot (CSV)", "modules.batch_processor", "batch_processor"),
        ("Chercheur Autonome (Web)", "modules.web_researcher", "web_researcher"),
        ("Acheteur Sceptique Multi-Agents", "modules.agent_critic", "buyer_critic"),
        ("Auditeur DNS & Anti-Spam", "modules.domain_auditor", "domain_auditor"),
        ("CRM SQLite & Analytics", "modules.pipeline_tracker", "pipeline_tracker"),
        ("Triage des Réponses Entrantes", "modules.reply_triage", "reply_triage"),
        ("Découvreur de Leads Web", "modules.lead_searcher", "lead_searcher"),
        ("Cadence Stratégique", "modules.cadence_engine", "cadence_engine"),
        ("Adaptateur Multi-Personas", "modules.persona_adapter", "persona_adapter"),
        ("Simulateur ROI & Forecaster", "modules.campaign_forecaster", "campaign_forecaster"),
        ("Auto-Évolution des Prompts", "modules.auto_evolver", "prompt_evolver"),
        ("Radar Signaux Live News", "modules.live_signal_monitor", "live_signal_monitor"),
        ("Générateur One-Pager VIP", "modules.one_pager_generator", "one_pager_generator"),
        ("Connecteur CRM & Webhooks", "modules.crm_exporter", "crm_exporter"),
        ("Espion Technographique", "modules.tech_stack_spy", "tech_stack_spy"),
        ("Battlecard Téléphonique", "modules.voice_battlecard", "voice_battlecard"),
        ("Moteur ABM Multi-Contacts", "modules.abm_syndicate", "abm_syndicate"),
        ("Calculateur Perte & ROI", "modules.roi_calculator", "roi_calculator"),
    ]

    success_count = 0
    t0 = time.time()

    for label, mod_name, attr_name in modules_to_test:
        try:
            mod = __import__(mod_name, fromlist=[attr_name])
            obj = getattr(mod, attr_name, None)
            if obj is not None:
                print(f"  ✅ [OPÉRATIONNEL] {label.ljust(35)} : Chargé avec succès")
                success_count += 1
            else:
                print(f"  ⚠️ [ATTENTION]   {label.ljust(35)} : Attribut manquant")
        except Exception as e:
            print(f"  ❌ [ERREUR]       {label.ljust(35)} : {e}")

    total_time = round(time.time() - t0, 2)
    score = int((success_count / len(modules_to_test)) * 100)

    print("\n" + "-"*75)
    print(f"📊 RÉSULTAT DU BENCHMARK : {success_count}/{len(modules_to_test)} Modules Actifs ({score}%)")
    print(f"⚡ Temps d'exécution du diagnostic : {total_time}s")
    if score == 100:
        print("🏆 STATUT GLOBAL : SYSTÈME STRATOSPHÉRIQUE 100% VALIDE POUR PRODUCTION")
    else:
        print("⚠️ STATUT GLOBAL : Quelques modules nécessitent une vérification")
    print("="*75 + "\n")

if __name__ == "__main__":
    run_healthcheck()
