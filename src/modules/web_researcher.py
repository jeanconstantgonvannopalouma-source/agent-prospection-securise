"""
AGENT CHERCHEUR AUTONOME (WEB RESEARCHER)
Analyse automatique de sites web et extraction d'intelligence commerciale
"""
import os
import re
import json
import logging
import urllib.request
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

class WebResearcher:
    """Agent autonome qui analyse un site web et construit une fiche d'intelligence B2B"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = None
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                for candidate in ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest"]:
                    try:
                        self.model = genai.GenerativeModel(candidate)
                        break
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"Erreur init Gemini Researcher: {e}")

    def fetch_website_summary(self, url_or_domain: str) -> str:
        """Télécharge et extrait le texte brut principal d'une page web"""
        if not url_or_domain.startswith("http"):
            url = f"https://{url_or_domain}"
        else:
            url = url_or_domain

        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=6) as response:
                html = response.read().decode('utf-8', errors='ignore')
                
                # Nettoyage du HTML pour ne garder que le contenu textuel
                clean_text = re.sub(r'<script.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<style.*?</style>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                return clean_text[:4000] # On garde les 4000 premiers caractères utiles
        except Exception as e:
            logger.warning(f"Impossible de scraper directement {url_or_domain}: {e}")
            return f"Entreprise connue sous le nom de {url_or_domain}."

    def analyze_company(self, company_name_or_url: str) -> Dict[str, Any]:
        """Génère une fiche d'intelligence commerciale complète via Gemini"""
        raw_web_data = self.fetch_website_summary(company_name_or_url)
        
        prompt = f"""
Tu es un analyste en intelligence commerciale B2B d'élite.
Analyse les informations suivantes concernant l'entreprise '{company_name_or_url}' :

DONNÉES DU SITE / CONTEXTE :
{raw_web_data}

Construis une fiche d'intelligence stratégique pour prospecter cette entreprise.
Réponds STRICTEMENT au format JSON valide :
{{
    "company_summary": "Ce que fait l'entreprise en 1 phrase concise",
    "target_market": "Leur cible principale (ex: PME, Grands Comptes, E-commerce...)",
    "estimated_industry": "Secteur d'activité précis",
    "probable_pain_point": "Leur plus grand défi de croissance actuel",
    "killer_hook_angle": "L'angle d'accroche personnalisé le plus percutant pour les contacter"
}}
"""
        if not self.model:
            return {
                "company_summary": f"Entreprise opérant dans le secteur B2B ({company_name_or_url}).",
                "target_market": "Clients B2B",
                "estimated_industry": "Tech / B2B",
                "probable_pain_point": "Acquisition de nouveaux comptes qualifiés",
                "killer_hook_angle": "Optimisation de la productivité commerciale"
            }

        try:
            resp = self.model.generate_content(prompt)
            clean_txt = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean_txt)
        except Exception as e:
            logger.error(f"Erreur extraction intelligence: {e}")
            return {
                "company_summary": f"Activité de {company_name_or_url}",
                "target_market": "Marché B2B",
                "estimated_industry": "Services B2B",
                "probable_pain_point": "Génération de leads",
                "killer_hook_angle": "Gain de temps sur la prospection"
            }

web_researcher = WebResearcher()
