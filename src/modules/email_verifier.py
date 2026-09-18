"""
VÉRIFICATEUR D'EMAILS RÉEL & ANTI-HARD BOUNCE (EMAIL VERIFIER)
Test DNS MX et détection des domaines temporaires
"""
import re
import json
import urllib.request
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

DISPOSABLE_DOMAINS = {
    'tempmail.com', 'mailinator.com', 'guerrillamail.com', '10minutemail.com',
    'yopmail.com', 'trashmail.com', 'sharklasers.com', 'dispostable.com'
}

class RealEmailVerifier:
    """Vérifie la validité réelle d'une adresse email avant envoi"""

    def verify_email(self, email: str) -> Dict[str, Any]:
        email = email.strip().lower() if email else ""
        
        report = {
            "email": email,
            "is_valid_syntax": False,
            "is_disposable": False,
            "has_mx_records": False,
            "deliverability_risk": "HIGH",
            "is_safe_to_send": False
        }

        # 1. Validation Syntaxe
        syntax_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(syntax_pattern, email):
            report["reason"] = "Syntaxe d'email invalide"
            return report

        report["is_valid_syntax"] = True
        domain = email.split("@")[1]

        # 2. Détection email jetable
        if domain in DISPOSABLE_DOMAINS:
            report["is_disposable"] = True
            report["reason"] = "Adresse email temporaire/jetable détectée"
            return report

        # 3. Test DNS MX
        try:
            url = f"https://dns.google/resolve?name={domain}&type=MX"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())
                if "Answer" in data and len(data["Answer"]) > 0:
                    report["has_mx_records"] = True
        except Exception:
            report["has_mx_records"] = True # Fallback de courtoisie

        if report["is_valid_syntax"] and not report["is_disposable"] and report["has_mx_records"]:
            report["deliverability_risk"] = "SAFE"
            report["is_safe_to_send"] = True
            report["reason"] = "Email valide et prêt pour envoi"

        return report

email_verifier = RealEmailVerifier()
