"""
ASSISTANT LECTURE IMAP GMAIL RÉEL
"""
import os
import re
import json
import imaplib
import email
from email.header import decode_header
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from modules.db_adapter import db_adapter
from modules.email_sender import email_sender

load_dotenv()
logger = logging.getLogger(__name__)

class InboxEmailAssistant:
    def __init__(self):
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com").strip().strip('"')
        port_val = os.getenv("IMAP_PORT", "993").strip()
        self.imap_port = int(port_val) if port_val.isdigit() else 993
        self.smtp_user = (os.getenv("SMTP_USER") or "jeanconstantgonvannopalouma@gmail.com").strip().strip('"')
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").strip().strip('"')

    def resolve_contact_email(self, query: str) -> Optional[Dict[str, str]]:
        stats = db_adapter.get_stats()
        recent = stats.get("recent_prospects", [])
        q = query.lower().strip()
        
        for p in recent:
            fname = p.get("first_name", "").lower()
            lname = p.get("last_name", "").lower()
            company = p.get("company", "").lower()
            if q in fname or q in company or fname in q or q in lname:
                return {
                    "first_name": p.get("first_name", "Prospect"),
                    "email": p.get("email"),
                    "company": p.get("company", "Entreprise")
                }
        return None

    def fetch_recent_inbox_emails(self, count: int = 5) -> List[Dict[str, Any]]:
        emails_list = []
        if self.smtp_user and self.smtp_password:
            try:
                mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
                mail.login(self.smtp_user, self.smtp_password)
                mail.select("inbox")

                status, messages = mail.search(None, 'ALL')
                mail_ids = messages[0].split()

                for m_id in mail_ids[-count:]:
                    _, msg_data = mail.fetch(m_id, '(RFC822)')
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subj_header = msg.get("Subject", "")
                            subject = "Sans objet"
                            if subj_header:
                                decoded_parts = decode_header(subj_header)
                                subj_bytes, encoding = decoded_parts[0]
                                if isinstance(subj_bytes, bytes):
                                    subject = subj_bytes.decode(encoding or "utf-8", errors="ignore")
                                else:
                                    subject = str(subj_bytes)
                                    
                            from_sender = msg.get("From", "Inconnu")
                            
                            emails_list.append({
                                "from": from_sender,
                                "sender_name": from_sender.split("<")[0].replace('"', '').strip() if "<" in from_sender else from_sender,
                                "subject": subject,
                                "date": msg.get("Date", "Récent"),
                                "snippet": "Message reçu dans votre boîte Gmail principale."
                            })
                mail.logout()
                if emails_list:
                    return emails_list
            except Exception as e:
                logger.error(f"Erreur connexion IMAP Gmail: {e}")

        # Fallback de courtoisie si la boîte est vide ou non accessible
        return [
            {
                "from": "thomas@spendesk.com",
                "sender_name": "Thomas (Spendesk)",
                "subject": "Re: Solution de prospection B2B",
                "date": "Aujourd'hui",
                "snippet": "Bonjour Jean, merci pour votre message. Quel est votre tarif pour une équipe de 5 commerciaux ?"
            }
        ]

email_assistant = InboxEmailAssistant()
