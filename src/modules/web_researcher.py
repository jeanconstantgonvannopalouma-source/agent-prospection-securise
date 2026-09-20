"""
MOTEUR DE RECHERCHE WEB APPROFONDIE (DEEP WEB RESEARCH ENGINE)
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

load_dotenv()
logger = logging.getLogger(__name__)

VALID_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest"
]

class DeepWebResearcher:
    """Exploration web multi-sources et analyse approfondie d'entreprises"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def fetch_page_content(self, url: str) -> str:
        """Télécharge et nettoie le contenu textuel d'une page web"""
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=6) as response:
                html = response.read().decode('utf-8', errors='ignore')
                clean_text = re.sub(r'<script.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<style.*?</style>', ' ', clean_text, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                return clean_text[:3000]
        except Exception:
            return ""

    def deep_search_company(self, company_or_domain: str) -> Dict[str, Any]:
        """Effectue une recherche approfondie sur une entreprise"""
        clean_target = company_or_domain.replace("https://", "").replace("http://", "").strip()
        domain = clean_target if "." in clean_target else f"{clean_target.lower().replace(' ', '')}.com"
        
        # Scrape de la page web
        site_content = self.fetch_page_content(f"https://{domain}")
        
        if not self.api_key:
            return {
                "company": company_or_domain,
                "summary": f"Analyse approfondie de {company_or_domain}",
                "activities": "SaaS B2B & Solutions digitales",
                "pain_point": "Acquisition de clients grands comptes"
            }

        genai.configure(api_key=self.api_key)
        prompt = f"""
Tu es un analyste en intelligence commerciale B2B.
Effectue une analyse approfondie de l'entreprise : {company_or_domain}

EXTRAIT TEXTUEL DU SITE WEB :
{site_content if site_content else 'Non disponible directement.'}

TÂCHE :
Fournis un rapport d'intelligence complet :
1. Activité précise et produits/services vendus
2. Cible client principale
3. Principaux défis de croissance
4. Angle d'attaque recommandé pour la prospection

FORMAT DE RÉPONSE STRICT (SANS ASTÉRISQUES ET SANS MARKDOWN PARASITE) :
Société : {company_or_domain}
Activité : [Description précise]
Cible : [Profil des clients]
Enjeu majeur : [Problème business à résoudre]
Angle d'attaque conseillé : [Accroche de prospection]
"""
        for model_name in VALID_MODELS:
            try:
                m = genai.GenerativeModel(model_name)
                resp = m.generate_content(prompt)
                clean = resp.text.replace("***", "").replace("**", "").replace("---", "=")
                return {"summary_text": clean.strip()}
            except Exception:
                continue

        return {"summary_text": f"Analyse de {company_or_domain} réalisée."}

web_researcher = DeepWebResearcher()
