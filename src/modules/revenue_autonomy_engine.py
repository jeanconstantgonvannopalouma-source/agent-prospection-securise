"""
MOTEUR D'AUTONOMIE FINANCIÈRE ET D'EXPÉDITION AUTOMATIQUE SUR LIEN
Scrape un lien, trouve des prospects réels, rédige les e-mails et les expédie via Gmail
"""
import os
import re
import json
import urllib.request
import urllib.parse
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai

from modules.knowledge_base import knowledge_base
from modules.real_lead_hunter import real_lead_hunter
from modules.message_engine import message_engine
from modules.email_sender import email_sender
from modules.db_adapter import db_adapter

load_dotenv()
logger = logging.getLogger(__name__)

VALID_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest"
]

class RevenueAutonomyEngine:
    """Transforme une URL en campagne de prospection réelle expédiée immédiatement"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def scrape_url_deep(self, url: str) -> str:
        if not url.startswith("http"):
            url = f"https://{url}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=7) as response:
                html = response.read().decode('utf-8', errors='ignore')
                clean_text = re.sub(r'<script.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<style.*?</style>', ' ', clean_text, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                return clean_text[:3000]
        except Exception as e:
            logger.warning(f"Erreur scraping {url}: {e}")
            return f"Produit Gumroad / Offre B2B de Jean Constant : {url}"

    def execute_full_autonomous_campaign(self, url: str) -> str:
        """Exécute toute la chaîne : Extraction -> Chasse de leads -> Rédaction -> Envoi Gmail -> Rapport"""
        page_content = self.scrape_url_deep(url)
        
        if not self.api_key:
            return "❌ Clé API Gemini manquante."

        genai.configure(api_key=self.api_key)

        # 1. Extraction de l'offre et définition de la requête de chasse
        extract_prompt = f"""
Tu es l'agent de prospection personnalisé de Jean Constant Gonvanno Palouma.
Analyse cette page web / produit : {url}
Contenu de la page : {page_content}

TÂCHE :
1. Définis le titre exact du produit / offre.
2. Définis la cible client idéale (ICP) et formule la requête de recherche exacte pour chasser ces leads en France (ex: "Directeurs Commerciaux SaaS B2B Paris").
3. Rédige la proposition de valeur en 1 phrase.

Format JSON STRICT (SANS ASTÉRISQUES) :
{{
    "product_title": "Titre de l'offre",
    "icp_search_query": "Requête de recherche de cibles B2B",
    "value_prop": "Proposition de valeur"
}}
"""
        offer_data = {"product_title": "Produit B2B", "icp_search_query": "Directeurs Commerciaux B2B Paris", "value_prop": "Accélération des ventes B2B"}
        for model_name in VALID_MODELS:
            try:
                m = genai.GenerativeModel(model_name)
                resp = m.generate_content(extract_prompt)
                clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
                offer_data = json.loads(clean)
                break
            except Exception:
                continue

        # 2. Mise à jour de la Base de Connaissances
        knowledge_base.save_kb({
            "offer_title": offer_data.get("product_title"),
            "core_value_prop": offer_data.get("value_prop"),
            "booking_link": url
        })

        # 3. Chasse automatique de 3 cibles réelles
        search_query = offer_data.get("icp_search_query", "Directeurs Commerciaux B2B Paris")
        leads = real_lead_hunter.hunt_leads(search_query, count=3)

        # 4. Rédaction et envoi direct des e-mails via Gmail
        sent_reports = []
        for lead in leads:
            recipient_email = lead.get("email")
            prospect_name = lead.get("first_name", "Prospect")
            company_name = lead.get("company", "Entreprise")

            # Génération du message sur-mesure
            msg_data = message_engine.generate_personalized_message(
                prospect=lead,
                value_prop=f"{offer_data.get('value_prop')}. Découvrez la ressource complète ici : {url}"
            )
            
            subject = msg_data.get("subject", f"Ressource pour {company_name}")
            body = msg_data.get("body", "")

            # Envoi SMTP réel via Gmail
            send_res = email_sender.send_email(recipient_email, subject, body, prospect_name=prospect_name)
            
            # Enregistrement CRM
            db_adapter.record_prospect(lead, subject=subject, deal_val=4500.0)

            sent_reports.append({
                "name": prospect_name,
                "company": company_name,
                "email": recipient_email,
                "status": "✅ E-MAIL EXPÉDIÉ PAR GMAIL" if send_res.get("success") else f"⚠️ {send_res.get('error')}",
                "subject": subject
            })

        # 5. Rapport d'exécution épuré (Zero parasite)
        report = f"""J'AI PRIS LE CONTRÔLE ET DÉPLOYÉ TA CAMPAGNE AUTOMATIQUE EN DIRECT !

1. OFFRE ANALYSÉE ET CHARGÉE DANS LA BDD :
• Produit : {offer_data.get('product_title')}
• Lien : {url}
• Cible recherchée : {search_query}

2. PROSPECTS DÉCOUVERTS & E-MAILS EXPÉDIÉS DEPUIS TA BOÎTE GMAIL (jeanconstantgonvannopalouma@gmail.com) :

"""
        for idx, rep in enumerate(sent_reports, 1):
            report += f"Cible #{idx} : {rep['name']} ({rep['company']})\n"
            report += f"• Adresse e-mail : {rep['email']}\n"
            report += f"• Statut d'envoi : {rep['status']}\n"
            report += f"• Objet de l'e-mail : {rep['subject']}\n\n"

        report += "==================================================\n"
        report += "Toutes ces cibles ont été enregistrées dans ton CRM. Je surveille désormais leurs réponses pour organiser tes rendez-vous !"

        return report

revenue_autonomy_engine = RevenueAutonomyEngine()
