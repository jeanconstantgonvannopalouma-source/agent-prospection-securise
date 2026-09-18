"""
MOTEUR D'ENVOI SMTP RÉEL GMAIL
"""
import os
import smtplib
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class StratosphericEmailSender:
    def __init__(self):
        self.smtp_host = (os.getenv("SMTP_SERVER") or os.getenv("SMTP_HOST") or "smtp.gmail.com").strip().strip('"')
        port_val = os.getenv("SMTP_PORT", "587").strip()
        self.smtp_port = int(port_val) if port_val.isdigit() else 587
        self.smtp_user = (os.getenv("SMTP_USER") or "jeanconstantgonvannopalouma@gmail.com").strip().strip('"')
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").strip().strip('"')
        self.sender_email = self.smtp_user
        self.sender_name = os.getenv("EMAIL_FROM_NAME", "Jean Constant Gonvanno Palouma").strip().strip('"')
        
        dry_run_str = os.getenv("DRY_RUN", "false").strip().lower()
        self.is_dry_run = dry_run_str in ["true", "1", "yes"]

    def send_email(self, recipient_email: str, subject: str, body_text: str, prospect_name: str = "Prospect") -> Dict[str, Any]:
        if not recipient_email or "@" not in recipient_email:
            return {"success": False, "error": "Adresse e-mail destinataire invalide"}

        # Signature officielle
        signature = "\n\n--\nJean Constant Gonvanno Palouma\n+33 6 20 07 81 93\njeanconstantgonvannopalouma@gmail.com"
        full_body = body_text + signature if signature not in body_text else body_text

        if self.is_dry_run:
            logger.info(f"🧪 [SIMULATION D'ENVOI] Vers: {recipient_email} | Sujet: '{subject}'")
            return {
                "success": True,
                "mode": "simulation",
                "recipient": recipient_email,
                "subject": subject,
                "note": "DRY_RUN=true actif dans .env. Passe DRY_RUN=false pour envoyer de vrais emails."
            }

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.sender_name} <{self.sender_email}>"
            msg["To"] = recipient_email

            part = MIMEText(full_body, "plain", "utf-8")
            msg.attach(part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=12) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())

            logger.info(f"✓ VRAI EMAIL ENVOYÉ À {recipient_email}")
            return {
                "success": True,
                "mode": "live_gmail_smtp",
                "recipient": recipient_email,
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error(f"❌ Erreur SMTP Gmail : {e}")
            return {"success": False, "error": str(e), "mode": "failed_smtp"}

email_sender = StratosphericEmailSender()
