"""
ESPION TECHNOGRAPHIQUE (TECH STACK & TOOLING INTELLIGENCE)
Détecte la stack technique et logicielle d'une entreprise pour personnaliser le pitch
"""
import os
import re
import json
import logging
import urllib.request
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

SIGNATURES = {
    "HubSpot": r"(hubspot|hs-scripts|hsforms)",
    "Salesforce / Pardot": r"(salesforce|pardot|mktoresp)",
    "Shopify": r"(shopify|cdn\.shopify\.com)",
    "WordPress / WooCommerce": r"(wp-content|wp-includes|woocommerce)",
    "Stripe": r"(js\.stripe\.com|stripe)",
    "Google Analytics 4": r"(googletagmanager\.com|gtag/js)",
    "Intercom": r"(intercom\.io|widget\.intercom\.io)",
    "Segment": r"(cdn\.segment\.com)",
    "Webflow": r"(assets\.website-files\.com|webflow)"
}

class TechStackSpy:
    """Analyse les technologies sous-jacentes d'un prospect"""

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
                logger.error(f"Erreur init TechSpy: {e}")

    def detect_technologies(self, domain_or_url: str) -> List[str]:
        """Scrape le code source HTML pour détecter les signatures d'outils"""
        if not domain_or_url.startswith("http"):
            url = f"https://{domain_or_url}"
        else:
            url = domain_or_url

        detected = []
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8', errors='ignore')
                for tool_name, pattern in SIGNATURES.items():
                    if re.search(pattern, html, re.IGNORECASE):
                        detected.append(tool_name)
        except Exception:
            pass

        return detected if detected else ["Stack SaaS Moderne (Standard Cloud)"]

    def generate_technographic_pitch(self, company_name: str, domain: str, raw_value_prop: str) -> Dict[str, Any]:
        """Formule une accroche basée sur les outils réels détectés"""
        techs = self.detect_technologies(domain)

        if not self.model:
            return {
                "detected_tools": techs,
                "technographic_angle": f"Intégration native avec votre écosystème ({', '.join(techs)})",
                "recommended_hook": f"J'ai vu que vous utilisiez {techs[0]} chez {company_name}."
            }

        prompt = f"""
Tu es un architecte commercial SaaS B2B.
Entreprise : {company_name} (Site : {domain})
Technologies détectées sur leur site : {', '.join(techs)}
Notre solution : {raw_value_prop}

TÂCHE :
1. Déduis leur niveau de maturité digitale.
2. Rédige un angle d'accroche valorisant la compatibilité ou le boost de leur stack actuelle (ex: "Décuplez la valeur de votre CRM {techs[0]}").

Format STRICT JSON :
{{
    "detected_tools": {json.dumps(techs)},
    "digital_maturity": "Élevée / Intermédiaire / Traditionnelle",
    "technographic_angle": "L'angle de vente basé sur leurs outils",
    "recommended_hook": "Accroche d'email citant leur stack sans faire 'espionnage lourd'"
}}
"""
        try:
            resp = self.model.generate_content(prompt)
            clean = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            return json.loads(clean)
        except Exception:
            return {
                "detected_tools": techs,
                "digital_maturity": "Intermédiaire",
                "technographic_angle": "Interopérabilité rapide",
                "recommended_hook": f"Notre plateforme se synchronise nativement avec votre environnement {techs[0]}."
            }

tech_stack_spy = TechStackSpy()
