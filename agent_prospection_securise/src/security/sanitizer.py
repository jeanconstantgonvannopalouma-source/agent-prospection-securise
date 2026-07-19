$content = @"
"""
Module de nettoyage avancé des données
Traite les données dangereuses de multiples façons
"""

import re
import logging
from typing import Any, Dict, List
import sys
from pathlib import Path
import html
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config

logger = logging.getLogger(__name__)

class DataSanitizer:
    """Nettoyage robuste et sécurisé des données"""
    
    # Patterns dangereux
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>',
    ]
    
    SQL_KEYWORDS = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'UNION', 'SELECT',
        '--', '/*', '*/', 'EXEC', 'EXECUTE', 'DECLARE', 'CAST',
    ]
    
    @staticmethod
    def sanitize_string(
        text: str,
        max_length: int = None,
        allow_newlines: bool = False,
        allow_special_chars: bool = False
    ) -> str:
        """
        Nettoie une chaîne de caractères de manière ULTRA robuste
        
        Args:
            text: Texte à nettoyer
            max_length: Longueur max
            allow_newlines: Autorise retours à la ligne
            allow_special_chars: Autorise caractères spéciaux
            
        Returns:
            Texte nettoyé
        """
        if not text or not isinstance(text, str):
            return ""
        
        if max_length is None:
            max_length = config.MAX_INPUT_LENGTH
        
        # Limite la longueur
        text = text[:max_length]
        
        # ===== SUPPRIME CARACTÈRES DANGEREUX =====
        # Supprime les caractères de contrôle (sauf newlines si autorisés)
        if allow_newlines:
            text = ''.join(
                char for char in text
                if ord(char) >= 32 or char in '\n\t\r'
            )
        else:
            text = ''.join(
                char for char in text
                if ord(char) >= 32 or char == '\t'
            )
        
        # ===== ÉCHAPPE HTML =====
        text = html.escape(text, quote=True)
        
        # ===== SUPPRIME SCRIPTS =====
        for pattern in DataSanitizer.XSS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # ===== SUPPRIME CARACTÈRES NULL =====
        text = text.replace('\x00', '')
        
        # ===== SUPPRIME ESPACES EXCESSIFS =====
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def sanitize_json(data: Any) -> Any:
        """
        Nettoie un objet JSON récursivement
        
        Args:
            data: Objet JSON à nettoyer
            
        Returns:
            Objet nettoyé
        """
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                # Nettoie la clé
                clean_key = DataSanitizer.sanitize_string(str(key), max_length=255)
                # Nettoie la valeur
                clean_value = DataSanitizer.sanitize_json(value)
                cleaned[clean_key] = clean_value
            return cleaned
        
        elif isinstance(data, list):
            return [DataSanitizer.sanitize_json(item) for item in data]
        
        elif isinstance(data, str):
            return DataSanitizer.sanitize_string(data)
        
        elif isinstance(data, (int, float, bool, type(None))):
            return data
        
        else:
            return str(data)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Nettoie un nom de fichier
        
        Args:
            filename: Nom du fichier
            
        Returns:
            Nom nettoyé et sûr
        """
        if not filename:
            return "file"
        
        # Supprime les chemins
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Garde seulement caractères sûrs
        filename = re.sub(r'[^\w\-\.]', '', filename)
        
        # Limite la longueur
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename or "file"
    
    @staticmethod
    def remove_sql_keywords(text: str) -> bool:
        """
        Vérifie la présence de mots-clés SQL dangereux
        
        Args:
            text: Texte à vérifier
            
        Returns:
            True si dangereux détecté
        """
        if not text:
            return False
        
        text_upper = text.upper()
        
        for keyword in DataSanitizer.SQL_KEYWORDS:
            # Vérifie les mots entiers
            if re.search(r'\b' + keyword + r'\b', text_upper):
                logger.warning(f"⚠️ Keyword SQL détecté: {keyword}")
                return True
        
        return False
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Nettoie une adresse email"""
        if not email:
            return ""
        
        email = email.strip().lower()
        
        # Supprime caractères dangereux
        email = re.sub(r'[^\w\.\-@]', '', email)
        
        return email[:255]
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """Nettoie un numéro de téléphone"""
        if not phone:
            return ""
        
        phone = phone.strip()
        
        # Garde seulement chiffres, +, -, ()
        phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
        
        # Supprime espaces
        phone = phone.replace(' ', '')
        
        return phone[:20]
    
    @staticmethod
    def sanitize_url(url: str) -> str:
        """Nettoie une URL"""
        if not url:
            return ""
        
        url = url.strip()
        
        # Supprime les schemes dangereux
        if url.lower().startswith(('javascript:', 'data:', 'vbscript:')):
            logger.warning(f"⚠️ Scheme dangereux détecté: {url[:50]}")
            return ""
        
        return url[:2000]
    
    @staticmethod
    def sanitize_dict(data: Dict, allowed_keys: List[str] = None) -> Dict:
        """
        Nettoie un dictionnaire complètement
        
        Args:
            data: Dictionnaire à nettoyer
            allowed_keys: Clés autorisées (None = toutes)
            
        Returns:
            Dictionnaire nettoyé
        """
        if not isinstance(data, dict):
            return {}
        
        cleaned = {}
        
        for key, value in data.items():
            # Vérifie les clés autorisées
            if allowed_keys and key not in allowed_keys:
                logger.debug(f"⚠️ Clé non autorisée ignorée: {key}")
                continue
            
            # Nettoie récursivement
            if isinstance(value, dict):
                cleaned[key] = DataSanitizer.sanitize_dict(value, allowed_keys)
            elif isinstance(value, list):
                cleaned[key] = [DataSanitizer.sanitize_json(item) for item in value]
            elif isinstance(value, str):
                cleaned[key] = DataSanitizer.sanitize_string(value)
            else:
                cleaned[key] = value
        
        return cleaned

# Instance globale
sanitizer = DataSanitizer()

__all__ = ['sanitizer', 'DataSanitizer']
"@

$content | Out-File -FilePath "src\security\sanitizer.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\security\sanitizer.py" -ForegroundColor Green