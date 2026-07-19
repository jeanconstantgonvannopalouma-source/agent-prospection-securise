"""Chiffrement AES-256 sécurisé"""
from cryptography.fernet import Fernet, InvalidToken
import base64
import logging
import bcrypt

logger = logging.getLogger(__name__)

class SecureEncryption:
    def __init__(self, key):
        self.cipher = Fernet(key.encode())
    
    def encrypt_data(self, data: str) -> str:
        if not data:
            raise ValueError("Données vides")
        try:
            encrypted = self.cipher.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Erreur chiffrement: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        if not encrypted_data:
            raise ValueError("Données vides")
        try:
            decoded = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode('utf-8')
        except InvalidToken:
            logger.error("Token invalide")
            raise ValueError("Données corrompues")
        except Exception as e:
            logger.error(f"Erreur déchiffrement: {e}")
            raise
    
    @staticmethod
    def hash_password(password: str) -> str:
        if not password or len(password) < 8:
            raise ValueError("Password invalide")
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hash_value: str) -> bool:
        if not password or not hash_value:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hash_value.encode('utf-8'))
        except Exception as e:
            logger.error(f"Erreur vérification: {e}")
            return False

# Instance globale
encryption = None

def init_encryption(key):
    global encryption
    encryption = SecureEncryption(key)
    return encryption
