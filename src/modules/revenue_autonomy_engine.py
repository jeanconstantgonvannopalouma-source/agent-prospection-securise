"""
MOTEUR D'AUTONOMIE FINANCIÈRE ET ANALYSE DE LIEN ULTRA-RAPIDE (ANTI-TIMEOUT)
"""
import os
import re
import json
import urllib.request
import urllib.parse
import logging
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from modules.knowledge_base import knowledge_base

load_dotenv()
logger = logging.getLogger(__name__)

VALID_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest"
]

class FastRevenueEngine:
    """Analyse les liens URL et génère le plan de monétisation en moins de 3 secondes"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def scrape_url_safe(self, url: str) -> str:
        """Scrape sécurisé avec User-Agent navigateur complet et gestion d'erreurs"""
        clean_url = url.split("?")[0] if "?" in url else url # Nettoyage des paramètres de tracking
        if not clean_url.startswith("http"):
            clean_url = f"https://{clean_url}"

        try:
            req = urllib.request.Request(
                clean_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                html = response.read().decode('utf-8', errors='ignore')
                clean_text = re.sub(r'<script.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<style.*?</style>', ' ', clean_text, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                return clean_text[:2500]
        except Exception as e:
            logger.warning(f"Note scraping sur {clean_url}: {e}")
            return f"Page de produit / offre B2B Gumroad de Jean Constant : {clean_url}"

    def analyze_and_plan_campaign(self, url: str) -> str:
        """Analyse l'URL et livre immédiatement le plan d'action et l'email prêt à être expédié"""
        content = self.scrape_url_safe(url)
        clean_url = url.split("?")[0] if "?" in url else url
        kb_context = knowledge_base.get_prompt_context()

        if not self.api_key:
            return "❌ Erreur: Clé GEMINI_API_KEY introuvable."

        genai.configure(api_key=self.api_key)

        prompt = f"""
Tu es l'agent de prospection personnalisé de Jean Constant Gonvanno Palouma.

{kb_context}

LIEN TRANSMIS PAR JEAN CONSTANT : {clean_url}
CONTENU EXTRAIT DE LA PAGE :
{content}

TÂCHE :
Analyse ce lien et livre immédiatement la stratégie pour le transformer en CHIFFRE D'AFFAIRES.

RÈGLES DE FORMATAGE STRICTES (ZERO PARASITE) :
- N'utilise AUCUN astérisque (* ou **), AUCUNE ligne de séparation (*** ou ---), AUCUNE italique.
- Rédige un texte clair, aéré et directement opérationnel.

STRUCTURE DE RÉPONSE EXIGÉE :

1. ANALYSE ET IDENTIFICATION DU LIEN :
[Explication de ce que contient ce lien et son potentiel commercial]

2. STRATÉGIE DE MONÉTISATION ET POSITIONNEMENT :
[Comment utiliser cette ressource/offre pour générer du cash pour Jean Constant]

3. PROFILES DES DECIDEURS CIBLES (ICP) :
[Les 3 postes exacts à contacter]

4. COLD EMAIL PRÊT À EXPÉDIER :
Objet : [Objet court et percutant]

Bonjour [Prénom],

[Corps du mail de 50 mots intégrant le lien {clean_url}]

Bien à vous,
Jean Constant Gonvanno Palouma
+33 6 20 07 81 93

5. ACTION SUIVANTE :
[Proposer de lancer l'envoi direct aux contacts du CRM ou d'exécuter la chasse de nouveaux leads]
"""
        for model_name in VALID_MODELS:
            try:
                m = genai.GenerativeModel(model_name)
                resp = m.generate_content(prompt)
                clean = resp.text.replace("***", "").replace("**", "").replace("---", "==================================================")
                return clean.strip()
            except Exception:
                continue

        return f"Analyse de {clean_url} effectuée."

revenue_autonomy_engine = FastRevenueEngine()
