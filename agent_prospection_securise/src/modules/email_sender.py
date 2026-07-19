$content = @"
"""
Module d'envoi d'emails sécurisé
Gère l'envoi et le tracking des emails
"""

import logging
from typing import Optional, Dict, List
import sys
from pathlib import Path
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config
from security.validation import InputValidator
from security.sanitizer import DataSanitizer
from security.rate_limiter import rate_limiter
from database.models import Message, MessageStatus
from database.repositories import MessageRepository

logger = logging.getLogger(__name__)
validator = InputValidator()
sanitizer = DataSanitizer()

class EmailSender:
    """Gestionnaire d'envoi d'emails sécurisé"""
    
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.smtp_user = config.SMTP_USER
        self.smtp_password = config.SMTP_PASSWORD
        self.rate_limiter = rate_limiter
        
        logger.info(f"✓ EmailSender initialisé ({self.smtp_server}:{self.smtp_port})")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        message_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Envoie un email de manière sécurisée
        
        Args:
            to_email: Adresse destination
            subject: Sujet
            body: Corps du message
            message_id: ID du message en BD (optionnel)
            
        Returns:
            (success: bool, message: str)
        """
        
        # Rate limiting
        is_allowed, msg = self.rate_limiter.is_allowed(to_email)
        if not is_allowed:
            logger.warning(f"Rate limit email: {msg}")
            return False, msg
        
        # Valide l'email
        if not validator.validate_email(to_email):
            logger.error(f"❌ Email invalide: {to_email}")
            return False, "Email invalide"
        
        # Nettoie les données
        subject = sanitizer.sanitize_string(subject, max_length=255)
        body = sanitizer.sanitize_string(body)
        
        try:
            # Crée le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
            
            # Corps HTML et texte
            text_part = MIMEText(body, 'plain', 'utf-8')
            html_part = MIMEText(self._convert_to_html(body), 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Envoie via SMTP
            if self._send_via_smtp(msg, to_email):
                logger.info(f"✓ Email envoyé: {to_email}")
                return True, "Email envoyé avec succès"
            else:
                logger.error(f"❌ Échec envoi email: {to_email}")
                return False, "Échec envoi email"
                
        except Exception as e:
            logger.error(f"❌ Erreur envoi email: {e}")
            return False, f"Erreur: {str(e)}"
    
    def _send_via_smtp(self, message, to_email: str) -> bool:
        """Envoie le message via SMTP"""
        try:
            # Connexion sécurisée
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, [to_email], message.as_string())
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Erreur authentication SMTP")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ Erreur SMTP: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur connexion SMTP: {e}")
            return False
    
    def _convert_to_html(self, text: str) -> str:
        """Convertit le texte en HTML"""
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    p {{ margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div style="max-width: 600px;">
                    {text.replace(chr(10), '<br>')}
                    <hr style="margin: 20px 0;">
                    <p style="font-size: 12px; color: #666;">
                        Email envoyé par Agent de Prospection
                    </p>
                </div>
            </body>
        </html>
        """
        return html

# Instance globale
email_sender = EmailSender()

__all__ = ['email_sender', 'EmailSender']
"@

$content | Out-File -FilePath "src\modules\email_sender.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\modules\email_sender.py" -ForegroundColor Green