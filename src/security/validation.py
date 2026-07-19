"""Validation robuste des entrées"""
import re
import logging
from email_validator import validate_email, EmailNotValidError

logger = logging.getLogger(__name__)

class InputValidator:
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')
    
    @staticmethod
    def validate_email(email: str) -> bool:
        if not email or not isinstance(email, str):
            return False
        if len(email) > 255:
            return False
        try:
            validate_email(email, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        if not phone or not isinstance(phone, str):
            return False
        if len(phone) > 20:
            return False
        return bool(InputValidator.PHONE_PATTERN.match(phone))
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        if not isinstance(text, str):
            return ""
        text = text[:max_length]
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t\r')
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    @staticmethod
    def validate_prospect_data(data: dict) -> tuple:
        errors = []
        
        required = ['email', 'first_name', 'company']
        for field in required:
            if field not in data or not data[field]:
                errors.append(f"Champ manquant: {field}")
        
        if 'email' in data and data['email']:
            if not InputValidator.validate_email(data['email']):
                errors.append(f"Email invalide: {data['email']}")
        
        if 'first_name' in data and data['first_name']:
            if len(data['first_name']) < 2:
                errors.append("Prénom trop court")
        
        return len(errors) == 0, errors

validator = InputValidator()
