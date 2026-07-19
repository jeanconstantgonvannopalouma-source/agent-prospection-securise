$content = @"
"""
Module de chiffrement sécurisé AES-256
Protège toutes les données sensibles
"""

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import os
import base64
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config

logger = logging.getLogger(__name__)

class SecureEncryption:
    """Chiffrement AES-256 sécurisé"""
    
    def __init__(self):
        """Initialise le chiffrement"""
        self.encryption_key = config.ENCRYPTION_KEY
        
        # Valide la clé
        if not self.encryption_key:
            raise ValueError("❌ ENCRYPTION_KEY manquante!")
        
        try:
            self.cipher = Fernet(self.encryption_key.encode())
            logger.info("✓ Chiffrement Fernet initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Fernet: {e}")
            raise
    
    def encrypt_data(self, data: str) -> str:
        """
        Chiffre les données sensibles
        
        Args:
            data: Texte à chiffrer
            
        Returns:
            Texte chiffré en base64
            
        Raises:
            ValueError: Si les données sont invalides
        """
        if not data:
            raise ValueError("❌ Données à chiffrer ne peuvent pas être vides")
        
        if not isinstance(data, str):
            data = str(data)
        
        try:
            # Chiffre
            encrypted = self.cipher.encrypt(data.encode('utf-8'))
            
            # Encode en base64
            encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
            
            logger.debug(f"✓ Données chiffrées ({len(data)} -> {len(encrypted_b64)} chars)")
            return encrypted_b64
            
        except Exception as e:
            logger.error(f"❌ Erreur chiffrement: {e}")
            raise ValueError(f"Erreur lors du chiffrement: {e}")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Déchiffre les données
        
        Args:
            encrypted_data: Données chiffrées en base64
            
        Returns:
            Texte déchiffré
            
        Raises:
            ValueError: Si données corrompues ou clé invalide
        """
        if not encrypted_data:
            raise ValueError("❌ Données à déchiffrer ne peuvent pas être vides")
        
        try:
            # Décode de base64
            decoded = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Déchiffre
            decrypted = self.cipher.decrypt(decoded)
            
            result = decrypted.decode('utf-8')
            logger.debug(f"✓ Données déchiffrées ({len(encrypted_data)} -> {len(result)} chars)")
            return result
            
        except InvalidToken:
            logger.error("❌ Token de chiffrement invalide - données corrompues!")
            raise ValueError("Données chiffrées corrompues ou clé invalide")
        except Exception as e:
            logger.error(f"❌ Erreur déchiffrement: {e}")
            raise ValueError(f"Erreur lors du déchiffrement: {e}")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash un mot de passe avec bcrypt (12 rounds)
        
        Args:
            password: Mot de passe à hasher
            
        Returns:
            Hash bcrypt
        """
        import bcrypt
        
        if not password or len(password) < 8:
            raise ValueError("❌ Mot de passe invalide (min 8 caractères)")
        
        try:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            logger.debug("✓ Mot de passe hashé")
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Erreur hashing password: {e}")
            raise
    
    @staticmethod
    def verify_password(password: str, hash_value: str) -> bool:
        """
        Vérifie un mot de passe contre son hash
        
        Args:
            password: Mot de passe à vérifier
            hash_value: Hash stocké
            
        Returns:
            True si match, False sinon
        """
        import bcrypt
        
        if not password or not hash_value:
            return False
        
        try:
            is_match = bcrypt.checkpw(
                password.encode('utf-8'),
                hash_value.encode('utf-8')
            )
            logger.debug(f"Vérification password: {is_match}")
            return is_match
        except Exception as e:
            logger.error(f"❌ Erreur vérification password: {e}")
            return False
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Génère une API key sécurisée"""
        import secrets
        key = secrets.token_urlsafe(length)
        logger.debug(f"✓ API key générée ({length} chars)")
        return key
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Génère un token sécurisé"""
        import secrets
        token = secrets.token_hex(length)
        logger.debug(f"✓ Token généré ({length} chars)")
        return token

# Instance globale
encryption = SecureEncryption()

__all__ = ['encryption', 'SecureEncryption']
"@

$content | Out-File -FilePath "src\security\encryption.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\security\encryption.py" -ForegroundColor Green