"""
CONSOLE DE PILOTAGE DE L'AGENT STRATOSPHÉRIQUE
"""
import sys
import os

# Ajout de src au path
sys.path.insert(0, os.path.abspath("src"))

from core.agent import agent

def demo_pipeline():
    print("\n" + "="*70)
    print("🚀 DÉMARRAGE DU PIPELINE DE PROSPECTION STRATOSPHÉRIQUE")
    print("="*70)

    # Simulation d'un prospect avec un signal d'intention réel
    prospect = {
        "first_name": "Sophie",
        "email": "sophie.martin@fintech-innov.io",
        "company": "Fintech Innov",
        "position": "Chief Revenue Officer",
        "industry": "Fintech & Open Banking",
        "notes": "Vient d'annoncer l'expansion de ses activités en Espagne et en Allemagne"
    }

    print(f"\n👤 [1] CIBLAGE DU PROSPECT : {prospect['first_name']} chez {prospect['company']}")
    print(f"💼 Poste : {prospect['position']} | Secteur : {prospect['industry']}")
    print(f"📡 Signal d'intention : {prospect['notes']}")
    
    print("\n⏳ Analyse & Génération du message par Gemini...")
    result = agent.process_prospect(
        prospect_raw=prospect,
        value_prop="Accélérer le go-to-market européen grâce à notre moteur de prospection multi-marchés",
        framework="PAS",
        auto_send=True
    )

    enriched = result["prospect"]
    msg = result["campaign_message"]
    qa = result["deliverability_analysis"]
    status = result["send_status"]

    print("\n" + "-"*70)
    print("📊 [2] ENRICHISSEMENT & SCORING ICP :")
    print(f"  • Score ICP Fit : {enriched['qualification_score']}/100")
    print(f"  • Défi détecté par l'IA : {enriched.get('top_pain_point')}")
    print(f"  • Angle d'attaque conseillé : {enriched.get('recommended_angle')}")

    print("\n✍️ [3] EMAIL HYPER-PERSONNALISÉ GÉNÉRÉ :")
    print(f"  📧 OBJET : {msg.get('subject')}")
    print(f"  🎯 ACCROCHE : {msg.get('hook_used')}")
    print("\n--- CONTENU ---")
    print(msg.get("body"))
    print("---------------")

    print("\n🛡️ [4] QUALITÉ & DÉLIVRABILITÉ :")
    print(f"  • Score Anti-Spam : {qa['deliverability_score']}/100 (Optimal: {qa['is_optimal']})")
    print(f"  • Nombre de mots : {qa['word_count']} mots")

    print("\n📨 [5] STATUT D'EXPÉDITION :")
    print(f"  • Mode : {status.get('mode')}")
    print(f"  • Statut : {'Succès' if status.get('success') else 'En attente'}")
    print("="*70 + "\n")

if __name__ == "__main__":
    demo_pipeline()
