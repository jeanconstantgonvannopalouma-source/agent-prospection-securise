"""
RADAR DE SIGNAUX D'ACTUALITÉ EN TEMPS RÉEL (LIVE SIGNAL MONITOR)
Interroge Google News RSS et extrait des déclencheurs de timing stratégique
"""
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import re
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

class LiveSignalMonitor:
    """Surveille l'actualité économique en direct et détecte les signaux d'achat"""

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
                logger.error(f"Erreur init Radar: {e}")

    def fetch_live_news(self, company_or_topic: str) -> List[Dict[str, str]]:
        """Récupère les dernières actualités Google News via flux RSS officiel"""
        query = urllib.parse.quote(company_or_topic)
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"
        
        articles = []
        try:
            req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall('.//item')[:3]:
                    title = item.find('title').text if item.find('title') is not None else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    articles.append({"title": title, "date": pub_date})
        except Exception as e:
            logger.warning(f"Impossible de récupérer le flux news pour {company_or_topic}: {e}")

        return articles

    def extract_timing_trigger(self, company_name: str) -> Dict[str, Any]:
        """Analyse l'actualité brute et formule le trigger de prospection"""
        news_items = self.fetch_live_news(company_name)
        
        if not news_items or not self.model:
            return {
                "detected_event": f"Développement continu des activités de {company_name}",
                "timing_urgency": "Modéré (Timing standard)",
                "recommended_cold_hook": f"J'ai vu vos récentes initiatives chez {company_name}."
            }

        prompt = f"""
Tu es un stratège en veille concurrentielle.
Voici les actualités récentes trouvées sur l'entreprise '{company_name}' :
{json.dumps(news_items, ensure_ascii=False)}

TÂCHE :
1. Identifie l'événement économique le plus marquant.
2. Évalue l'urgence du timing (Élevé / Modéré / Normal).
3. Rédige l'accroche d'actualité exacte à citer dans le premier email pour prouver que nous avons suivi leur actualité.

Format STRICT JSON :
{{
    "detected_event": "Résumé de l'événement clé",
    "timing_urgency": "Élevé (Opportunité immédiate)",
    "recommended_cold_hook": "Accroche percutante citant l'événement"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "detected_event": news_items[0]["title"],
                "timing_urgency": "Élevé",
                "recommended_cold_hook": f"Félicitations pour l'actualité récente : {news_items[0]['title'][:60]}..."
            }

live_signal_monitor = LiveSignalMonitor()
