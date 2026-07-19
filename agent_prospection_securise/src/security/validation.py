$content = @"
"""
Module de validation robuste et sécurisée
Valide TOUTES les entrées avant traitement
"""

import re
import logging
from typing import Any, List, Dict, Tuple
from email_validator import validate_email, EmailNotValidError
from urllib.parse import urlparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config

logger = logging.getLogger(__name__)

class InputValidator:
    """Validation sécurisée de toutes les entrées"""
    
    # ===== PATTERNS REGEX VALIDÉS =====
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    PHONE_PATTERN = re.compile(
        r'^\+?[1-9]\d{1,14}$'  # Format E.164 international
    )
    
    URL_PATTERN = re.compile(
        r'^https?://[^\s/$.?#].[^\s]*$'
    )
    
    # Caractères dangereux
    DANGEROUS_CHARS = r'[<>\"\\x00-\x08\x0B\x0C\x0E-\x1F]'
    
    # Patterns d'injection SQL (simple)
    SQL_KEYWORDS = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'UNION', 'SELECT', '--', '/*', '*/']
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valide une adresse email de façon complète
        
        Args:
            email: Adresse email à valider
            
        Returns:
            True si valide, False sinon
        """
        if not email or not isinstance(email, str):
            logger.warning(f"Email invalide (type): {type(email)}")
            return False
        
        if len(email) > config.MAX_EMAIL_LENGTH:
            logger.warning(f"Email trop long: {len(email)} chars")
            return False
        
        try:
            # Utilise email_validator library
            validate_email(email, check_deliverability=False)
            logger.debug(f"✓ Email valide: {email}")
            return True
        except EmailNotValidError as e:
            logger.warning(f"Email invalide: {email} - {e}")
            return False
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Valide un numéro de téléphone (format E.164)
        
        Args:
            phone: Numéro de téléphone
            
        Returns:
            True si valide
        """
        if not phone or not isinstance(phone, str):
            return False
        
        if len(phone) > config.MAX_PHONE_LENGTH:
            return False
        
        if InputValidator.PHONE_PATTERN.match(phone):
            logger.debug(f"✓ Téléphone valide: {phone}")
            return True
        
        logger.warning(f"Téléphone invalide: {phone}")
        return False
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Valide une URL
        
        Args:
            url: URL à valider
            
        Returns:
            True si valide
        """
        if not url or not isinstance(url, str):
            return False
        
        try:
            result = urlparse(url)
            is_valid = all([result.scheme in ['http', 'https'], result.netloc])
            
            if is_valid:
                logger.debug(f"✓ URL valide: {url[:50]}...")
            else:
                logger.warning(f"URL invalide: {url}")
            
            return is_valid
        except Exception as e:
            logger.warning(f"Erreur validation URL: {e}")
            return False
    
    @staticmethod
    def sanitize_string(
        text: str,
        max_length: int = None,
        allow_html: bool = False
    ) -> str:
        """
        Nettoie une chaîne de caractères (HYPER robuste)
        
        Args:
            text: Texte à nettoyer
            max_length: Longueur max (défaut: config.MAX_INPUT_LENGTH)
            allow_html: Autorise HTML (défaut: False)
            
        Returns:
            Texte nettoyé et sûr
        """
        if max_length is None:
            max_length = config.MAX_INPUT_LENGTH
        
        if not isinstance(text, str):
            return ""
        
        # Limite la longueur
        text = text[:max_length]
        
        # Supprime caractères de contrôle dangereux
        text = ''.join(
            char for char in text
            if ord(char) >= 32 or char in '\n\t\r'
        )
        
        # Supprime les balises HTML/Script (sauf si autorisé)
        if not allow_html:
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
            text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Supprime caractères dangereux
        text = re.sub(InputValidator.DANGEROUS_CHARS, '', text)
        
        # Supprime les espaces inutiles
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def check_sql_injection(text: str) -> bool:
        """
        Détecte les tentatives d'injection SQL (simple)
        
        Args:
            text: Texte à vérifier
            
        Returns:
            True si injection détectée, False sinon
        """
        if not text:
            return False
        
        text_upper = text.upper()
        
        for keyword in InputValidator.SQL_KEYWORDS:
            if keyword in text_upper:
                logger.warning(f"⚠️ Injection SQL potentielle détectée: {keyword}")
                return True
        
        return False
    
    @staticmethod
    def validate_prospect_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valide COMPLÈTEMENT les données d'un prospect
        
        Args:
            data: Dictionnaire des données
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Données doivent être un dictionnaire")
            return False, errors
        
        # ===== CHAMPS OBLIGATOIRES =====
        required_fields = {
            'email': 'Email',
            'first_name': 'Prénom',
            'company': 'Entreprise'
        }
        
        for field, label in required_fields.items():
            if field not in data or not data[field]:
                errors.append(f"❌ Champ obligatoire manquant: {label}")
        
        # ===== VALIDATION EMAIL =====
        if 'email' in data and data['email']:
            email = data['email'].strip()
            if not InputValidator.validate_email(email):
                errors.append(f"❌ Email invalide: {email}")
            else:
                data['email'] = email
        
        # ===== VALIDATION TÉLÉPHONE (optionnel) =====
        if 'phone' in data and data['phone']:
            phone = data['phone'].strip()
            if phone and not InputValidator.validate_phone(phone):
                errors.append(f"❌ Téléphone invalide: {phone}")
            data['phone'] = phone if phone else None
        
        # ===== VALIDATION PRÉNOMS =====
        if 'first_name' in data and data['first_name']:
            first_name = InputValidator.sanitize_string(data['first_name'], max_length=100)
            if len(first_name) < 2:
                errors.append("❌ Prénom trop court (min 2 caractères)")
            data['first_name'] = first_name
        
        if 'last_name' in data and data['last_name']:
            last_name = InputValidator.sanitize_string(data['last_name'], max_length=100)
            data['last_name'] = last_name
        
        # ===== VALIDATION ENTREPRISE =====
        if 'company' in data and data['company']:
            company = InputValidator.sanitize_string(data['company'], max_length=255)
            if len(company) < 2:
                errors.append("❌ Entreprise trop courte (min 2 caractères)")
            if InputValidator.check_sql_injection(company):
                errors.append("❌ Entreprise contient caractères suspects")
            data['company'] = company
        
        # ===== VALIDATION POSTE (optionnel) =====
        if 'job_title' in data and data['job_title']:
            job_title = InputValidator.sanitize_string(data['job_title'], max_length=150)
            data['job_title'] = job_title
        
        # ===== NETTOYAGE NOTES (optionnel) =====
        if 'notes' in data and data['notes']:
            notes = InputValidator.sanitize_string(data['notes'], max_length=1000)
            data['notes'] = notes
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.debug("✓ Données prospect validées avec succès")
        else:
            logger.warning(f"❌ Erreurs validation prospect: {errors}")
        
        return is_valid, errors

# Instance globale
validator = InputValidator()

__all__ = ['validator', 'InputValidator']
"@

$content | Out-File -FilePath "src\security\validation.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\security\validation.py" -ForegroundColor Green