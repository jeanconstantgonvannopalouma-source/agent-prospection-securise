"""
CONSOLE STRATOSPHÉRIQUE INTERACTIVE V14.0 (CLOSING ACCELERATION SUITE)
"""
import os
import sys
import time

sys.path.insert(0, os.path.abspath("src"))

from core.agent import agent
from modules.message_engine import message_engine
from modules.email_sender import email_sender
from modules.objection_handler import objection_handler
from modules.batch_processor import batch_processor
from modules.web_researcher import web_researcher
from modules.agent_critic import buyer_critic
from modules.domain_auditor import domain_auditor
from modules.pipeline_tracker import pipeline_tracker
from modules.reply_triage import reply_triage
from modules.lead_searcher import lead_searcher
from modules.cadence_engine import cadence_engine
from modules.persona_adapter import persona_adapter
from modules.campaign_forecaster import campaign_forecaster
from modules.auto_evolver import prompt_evolver
from modules.live_signal_monitor import live_signal_monitor
from modules.one_pager_generator import one_pager_generator
from modules.crm_exporter import crm_exporter
from modules.terminal_cockpit import terminal_cockpit
from modules.autopilot_daemon import autopilot_daemon
from modules.tech_stack_spy import tech_stack_spy
from modules.voice_battlecard import voice_battlecard
from modules.abm_syndicate import abm_syndicate
from modules.roi_calculator import roi_calculator
from modules.competitor_displacement import competitor_displacement
from modules.global_localizer import global_localizer
from modules.hiring_intent_radar import hiring_radar
from modules.vc_funding_tracker import vc_funding_tracker
from modules.voice_loom_generator import voice_loom_generator
from modules.visual_roi_generator import visual_roi_generator
from modules.intent_heat_matrix import intent_heat_matrix
from modules.meeting_synthesizer import meeting_synthesizer
from modules.warm_intro_engine import warm_intro_engine
from modules.ghosting_buster import ghosting_buster
from modules.mutual_action_plan import map_generator
from modules.smart_pricing_engine import smart_pricing_engine

def banner():
    print("\n" + "="*85)
    print("      🌌 AGENT DE PROSPECTION STRATOSPHÉRIQUE - V14.0 CLOSING SUITE")
    print(f"      Mode Envoi : {'🧪 SIMULATION SÉCURISÉE' if email_sender.is_dry_run else '🔴 SMTP RÉEL ACTIF'}")
    print(f"      Cerveau IA : {message_engine.active_model_name or 'Gemini 3.7 / 3.6 Flash'}")
    print("="*85)

def menu_ghosting_buster():
    print("\n--- 👻 GHOSTING BUSTER (RELANCES DE RUPTURE PSYCHOLOGIQUE) ---")
    name = input("Prénom du prospect silencieux [Ex: Thomas] : ") or "Thomas"
    comp = input("Entreprise [Ex: Spendesk] : ") or "Spendesk"
    last_topic = input("Dernier sujet abordé [Ex: Envoi de la proposition tarifaire] : ") or "Envoi de la proposition tarifaire"

    print(f"\n⏳ Génération des 3 tactiques de réactivation pour '{name}'...")
    res = ghosting_buster.generate_reactivation_tactics(name, comp, last_topic)

    print("\n" + "="*65)
    print("🎯 TACTIQUE #1 : L'EMAIL DE 9 MOTS (Framework Dean Jackson) :")
    print(f"\"{res.get('nine_word_email')}\"")
    
    print("\n🚪 TACTIQUE #2 : LA PORTE DE SORTIE SANS CULPABILITÉ (Breakup Email) :")
    print(f"{res.get('guilt_free_breakup')}")
    
    print("\n🎁 TACTIQUE #3 : VALEUR PURE SANS AUCUNE RELANCE (Zero Pressure) :")
    print(f"{res.get('zero_pressure_value')}")
    print("="*65)

def menu_map():
    print("\n--- 📋 MUTUAL ACTION PLAN (PLAN DE DÉCISION PARTAGÉ) ---")
    name = input("Prénom du sponsor : ") or "Alexandre"
    comp = input("Entreprise client : ") or "DataScale"
    days = int(input("Délai de déploiement visé (jours) [30] : ") or "30")

    print("\n⏳ Rédaction du Mutual Action Plan d'entreprise...")
    map_md = map_generator.generate_map(name, comp, days)

    filename = f"data/map_{comp.lower().replace(' ', '_')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(map_md)

    print("\n" + "="*65)
    print(f"🎉 MUTUAL ACTION PLAN GÉNÉRÉ DANS : '{filename}'")
    print("="*65)
    print(map_md[:700] + "\n\n[... Suite disponible dans le fichier Markdown généré ...]")
    print("="*65)

def menu_pricing():
    print("\n--- 🏷️ TARIFICATION DYNAMIQUE & SIMULATEUR DE REMISES ---")
    team = int(input("Taille de l'équipe commerciale du prospect [Ex: 6] : ") or "6")
    res = smart_pricing_engine.generate_tier_pricing(team)

    print("\n" + "="*65)
    print(f"📊 GRILLE TARIFAIRE SUR-MESURE (ÉQUIPE DE {team} COMMERCIAUX) :")
    print("="*65)
    for tier_name, data in res["tiers"].items():
        print(f"\n🌟 {tier_name.upper()}")
        print(f"  • Utilisateurs inclus  : {data['users']} sièges")
        print(f"  • Mensuel Sans Engagt  : {data['monthly_price_eur']:,.0f} € / mois")
        print(f"  • Annuel Facturé en 1x : {data['annual_price_eur']:,.0f} € / an (Économie: {data['annual_savings_eur']:,.0f} €)")
        print(f"  • Périmètre Fonctionnel: {data['scope']}")
    print("="*65)

def main():
    while True:
        banner()
        print("1. 🖥️  Cockpit Live V14.0 (Monitoring Temps Réel)")
        print("2. 🤖 Démon Autonome 24/7 (Pilote Automatique d'Arrière-Plan)")
        print("3. 👻 Ghosting Buster (Relances de Rupture Psychologique Anti-Silence)")
        print("4. 📋 Générer un Mutual Action Plan (MAP de Closing B2B)")
        print("5. 🏷️  Calculer une Grille Tarifaire Dynamique & Remises Annuelles")
        print("6. 🔥 Score d'Intention d'Achat Global (Buying Intent Heatmap /100)")
        print("7. 📝 Synthétiseur Post-Call & Email de Rebond (Meeting Recap)")
        print("8. 🤝 Moteur de Warm Intro & Textes Transférables (Forwardable Blurbs)")
        print("9. 💰 Tracker de Levées de Fonds & Signaux VC (Funding Runway)")
        print("10. 🎙️  Générer Script Vocal LinkedIn & Capsule Vidéo Loom 60s")
        print("11. 📊 Générer un Dashboard ROI Interactif HTML/SVG Personnalisé")
        print("12. ⚔️  Déloger un Concurrent (Lemlist, HubSpot, Apollo, Salesforce)")
        print("13. 🌍 Expansion Globale (Localisation US, UK, DE, ES, IT)")
        print("14. 💼 Radar d'Offres d'Emploi (Hiring Intent Scraper)")
        print("15. 🏢 Campagne ABM Syndicate (Encerclement 3 Décideurs)")
        print("16. 🎯 Prospection Apex (Radar Live News + Persona + Critique)")
        print("17. 🧮 Calculateur de Coût d'Inaction & ROI Financier (€)")
        print("18. 📞 Battlecard Téléphonique (Cold Calling Reflex Sheet)")
        print("19. 📄 Générer une Proposition VIP (One-Pager Markdown)")
        print("20. 📈 Simulateur de Revenus & ROI Prédictif (Forecaster)")
        print("21. 📥 Triage IA d'une réponse reçue (Inbound Triage)")
        print("22. 📂 Campagne par lot (Fichier CSV)")
        print("23. ⚡ Exporter le CRM ou déclencher un Webhook (Make / n8n)")
        print("24. 🚪 Quitter")
        
        choice = input("\n👉 Choix (1-24) : ").strip()
        
        if choice == "1": terminal_cockpit.render()
        elif choice == "2":
            if autopilot_daemon.is_running:
                autopilot_daemon.stop()
                print("\n🛑 Démon en pause.")
            else:
                autopilot_daemon.start()
                print("\n🟢 Démon actif en arrière-plan !")
        elif choice == "3": menu_ghosting_buster()
        elif choice == "4": menu_map()
        elif choice == "5": menu_pricing()
        elif choice == "6":
            comp = input("Entreprise [Pigment] : ") or "Pigment"
            res = intent_heat_matrix.compute_intent_heatmap(comp, "Recrute 5 SDRs", "Série B 30M€", "Expansion", ["HubSpot"])
            print(f"\nScore : {res.get('intent_heat_score')}/100 ({res.get('urgency_status')})")
        elif choice == "7":
            res = meeting_synthesizer.synthesize_call_notes("Thomas", "Spendesk", "Très intéressé, veut un devis sous 48h")
            print(f"\nProbabilité : {res.get('deal_probability_percent')}%\nEmail :\n{res.get('prospect_followup_email')}")
        elif choice == "8":
            res = warm_intro_engine.generate_forwardable_intro("Julien", "Sarah", "Doctolib", "IA B2B")
            print(f"\nTexte transférable :\n{res.get('forwardable_blurb')}")
        elif choice == "9":
            res = vc_funding_tracker.analyze_funding_context("Pennylane", "Série B (50M€)", "CEO")
            print(f"\nAccroche VC : \"{res.get('pitch_hook')}\"")
        elif choice == "10":
            res = voice_loom_generator.generate_voice_and_loom_script({"first_name": "Marc", "company": "Spendesk", "position": "VP"}, "IA")
            print(f"\nVocal LinkedIn : \"{res.get('linkedin_voice_note_script')}\"")
        elif choice == "11":
            p = visual_roi_generator.generate_html_roi_report("Swile", "Loïc")
            print(f"\n✅ Rapport HTML créé : {p}")
        elif choice == "12":
            res = competitor_displacement.generate_switch_pitch({"first_name": "Thomas", "company": "SaaS"}, "Lemlist", "IA B2B")
            print(f"\nEmail :\n{res.get('displacement_body')}")
        elif choice == "13":
            loc = global_localizer.localize_message("Boostez vos ventes", "Bonjour, accélérons vos RDVs.", "EN_US")
            print(f"\nSubject : {loc.get('localized_subject')}\nBody :\n{loc.get('localized_body')}")
        elif choice == "14":
            sig = hiring_radar.analyze_hiring_signals("PayFit", "3 SDRs")
            print(f"\nAccroche : \"{sig.get('hiring_hook')}\"")
        elif choice == "15":
            abm = abm_syndicate.generate_abm_campaign("Doctolib", "HealthTech", "Expansion", "IA B2B")
            print(f"\nCEO: {abm['economic_buyer']['subject']}\nVP Sales: {abm['champion']['subject']}")
        elif choice == "16":
            name = input("Prénom : ") or "Thomas"
            comp = input("Entreprise : ") or "Qonto"
            p = {"first_name": name, "company": comp, "position": "CEO", "industry": "FinTech"}
            res = message_engine.generate_personalized_message(p, "IA Commerciale")
            print(f"\nObjet : {res['subject']}\n\n{res['body']}")
            pipeline_tracker.record_prospect(p, subject=res['subject'])
        elif choice == "17":
            res = roi_calculator.compute_inaction_cost(6)
            print(f"\nPerte : {res['monthly_financial_waste_eur']:,.2f} €/mois")
        elif choice == "18":
            bc = voice_battlecard.generate_battlecard({"first_name": "Marc", "company": "Spendesk", "position": "VP"}, "IA")
            print(f"\nAccroche Vocale : \"{bc.get('opener_7_seconds')}\"")
        elif choice == "19":
            md = one_pager_generator.generate_one_pager({"first_name": "Alex", "company": "DataCorp", "position": "CEO"}, "IA")
            print(f"\n{md[:400]}...\n[One-Pager généré]")
        elif choice == "20":
            fc = campaign_forecaster.forecast_campaign(250, 4000.0)
            print(f"\nRDVs : {fc['projected_meetings']} | CA : {fc['projected_signed_revenue_eur']:,.2f} €")
        elif choice == "21":
            r = reply_triage.analyze_reply({"company": "Target"}, "Intéressé, appelons-nous.")
            print(f"\nIntention : {r['category']}\nRéponse : {r['suggested_reply']}")
        elif choice == "22":
            csv_f = input("Fichier [leads_exemple.csv] : ") or "leads_exemple.csv"
            batch_processor.process_csv_file(csv_f)
        elif choice == "23":
            path = crm_exporter.export_to_json()
            print(f"\n✅ Export généré dans '{path}'")
        elif choice == "24":
            if autopilot_daemon.is_running:
                autopilot_daemon.stop()
            print("\n👋 À bientôt sur l'Agent Stratosphérique V14.0 !\n")
            break
        else:
            print("❌ Option invalide.")
            
        input("\nAppuie sur Entrée pour continuer...")

if __name__ == "__main__":
    main()
