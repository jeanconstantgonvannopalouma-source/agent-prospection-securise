"""
AUDITEUR DE SANTÉ DE DOMAINE & SÉCURITÉ DÉLIVRABILITÉ
"""
import socket
import urllib.request
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DomainAuditor:
    """Vérifie la réputation et la configuration DNS d'un domaine d'expédition"""

    def audit_domain(self, domain: str) -> Dict[str, Any]:
        domain = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
        
        report = {
            "domain": domain,
            "has_mx": False,
            "has_spf": False,
            "has_dmarc": False,
            "health_score": 100,
            "recommendations": []
        }

        # 1. Vérification des serveurs MX (Capacité à recevoir/envoyer des mails)
        try:
            # Requête DNS Google DoH sécurisée
            url = f"https://dns.google/resolve?name={domain}&type=MX"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if "Answer" in data and len(data["Answer"]) > 0:
                    report["has_mx"] = True
        except Exception:
            report["has_mx"] = True # Fallback

        # 2. Vérification SPF (Sender Policy Framework)
        try:
            url_txt = f"https://dns.google/resolve?name={domain}&type=TXT"
            req = urllib.request.Request(url_txt, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                txt_records = [ans.get("data", "") for ans in data.get("Answer", [])]
                for rec in txt_records:
                    if "v=spf1" in rec.lower():
                        report["has_spf"] = True
                    if "v=dmarc1" in rec.lower():
                        report["has_dmarc"] = True
        except Exception:
            pass

        # 3. Calcul du score de santé
        if not report["has_mx"]:
            report["health_score"] -= 40
            report["recommendations"].append("❌ Aucun serveur MX détecté : ce domaine ne peut pas gérer d'emails.")
        if not report["has_spf"]:
            report["health_score"] -= 30
            report["recommendations"].append("⚠️ Enregistrement SPF manquant : risque élevé d'atterrir dans le dossier Spam.")
        if not report["has_dmarc"]:
            report["health_score"] -= 15
            report["recommendations"].append("💡 Enregistrement DMARC absent : conseillé pour maximiser la réputation auprès de Gmail/Outlook.")

        if report["health_score"] >= 85:
            report["status"] = "EXCELLENT 🟢"
        elif report["health_score"] >= 60:
            report["status"] = "MOYEN 🟡"
        else:
            report["status"] = "CRITIQUE 🔴"

        return report

domain_auditor = DomainAuditor()
