$content = @"
"""
Module d'authentification JWT
Génère et vérifie les tokens JWT de manière sécurisée
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config

logger = logging.getLogger(__name__)

class JWTAuth:
    """Authentification sécurisée par JWT"""
    
    def __init__(self):
        """Initialise l'authentification JWT"""
        self.secret = config.SECRET_KEY
        self.algorithm = config.JWT_ALGORITHM
        self.token_expiry_hours = config.JWT_EXPIRY_HOURS
        
        if not self.secret:
            raise ValueError("❌ SECRET_KEY manquante pour JWT")
        
        logger.info(f"✓ JWT Auth initialisé (algo: {self.algorithm}, expire: {self.token_expiry_hours}h)")
    
    def generate_token(
        self,
        user_id: str,
        email: str,
        roles: list = None,
        additional_claims: dict = None
    ) -> str:
        """
        Génère un JWT token sécurisé
        
        Args:
            user_id: ID utilisateur unique
            email: Email utilisateur
            roles: Liste des rôles (optionnel)
            additional_claims: Claims additionnels (optionnel)
            
        Returns:
            JWT token encodé
            
        Raises:
            ValueError: Si données invalides
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("❌ user_id invalide ou manquant")
        
        if not email or not isinstance(email, str):
            raise ValueError("❌ email invalide ou manquant")
        
        try:
            now = datetime.utcnow()
            expiry = now + timedelta(hours=self.token_expiry_hours)
            
            # ===== PAYLOAD SÉCURISÉ =====
            payload = {
                'user_id': user_id,
                'email': email,
                'roles': roles or ['user'],
                'iat': now,  # Issued At
                'exp': expiry,  # Expiration
                'nbf': now,  # Not Before
                'jti': self._generate_jti(),  # JWT ID unique
            }
            
            # Ajoute claims additionnels
            if additional_claims and isinstance(additional_claims, dict):
                payload.update(additional_claims)
            
            # Encode le token
            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            
            logger.info(f"✓ Token généré pour {email} (expire: {expiry})")
            return token
            
        except Exception as e:
            logger.error(f"❌ Erreur génération token: {e}")
            raise ValueError(f"Erreur génération token: {e}")
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Vérifie et décode un JWT token
        
        Args:
            token: JWT token à vérifier
            
        Returns:
            (is_valid, payload, message)
        """
        if not token or not isinstance(token, str):
            logger.warning("❌ Token invalide ou manquant")
            return False, None, "Token invalide ou manquant"
        
        try:
            # Décode et vérifie
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            
            logger.info(f"✓ Token vérifié pour {payload.get('email')}")
            return True, payload, "Token valide"
            
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ Token expiré")
            return False, None, "Token expiré"
        
        except jwt.InvalidTokenError as e:
            logger.warning(f"❌ Token invalide: {e}")
            return False, None, f"Token invalide: {str(e)}"
        
        except Exception as e:
            logger.error(f"❌ Erreur vérification token: {e}")
            return False, None, f"Erreur vérification: {str(e)}"
    
    def refresh_token(self, token: str) -> Tuple[bool, Optional[str], str]:
        """
        Rafraîchit un token valide
        
        Args:
            token: Token actuel
            
        Returns:
            (success, new_token, message)
        """
        is_valid, payload, msg = self.verify_token(token)
        
        if not is_valid:
            return False, None, f"Impossible rafraîchir: {msg}"
        
        try:
            new_token = self.generate_token(
                user_id=payload['user_id'],
                email=payload['email'],
                roles=payload.get('roles', ['user']),
            )
            
            logger.info(f"✓ Token rafraîchi pour {payload['email']}")
            return True, new_token, "Token rafraîchi"
            
        except Exception as e:
            logger.error(f"❌ Erreur rafraîchissement token: {e}")
            return False, None, f"Erreur: {str(e)}"
    
    def decode_token_unsafe(self, token: str) -> Optional[Dict]:
        """
        Décode un token SANS vérification (USE WITH CAUTION!)
        Uniquement pour lire les claims sans vérifier la signature
        
        Args:
            token: JWT token
            
        Returns:
            Payload ou None
        """
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            logger.warning("⚠️ Token décodé sans vérification (unsafe)")
            return payload
        except Exception as e:
            logger.error(f"❌ Erreur décodage: {e}")
            return None
    
    @staticmethod
    def _generate_jti() -> str:
        """Génère un JWT ID unique"""
        import secrets
        return secrets.token_hex(16)
    
    def get_token_info(self, token: str) -> Dict:
        """Retourne les informations d'un token"""
        is_valid, payload, msg = self.verify_token(token)
        
        if is_valid and payload:
            return {
                'is_valid': True,
                'user_id': payload.get('user_id'),
                'email': payload.get('email'),
                'roles': payload.get('roles', []),
                'expires_at': datetime.fromtimestamp(payload['exp']),
                'message': msg
            }
        else:
            return {
                'is_valid': False,
                'message': msg
            }

# Instance globale
jwt_auth = JWTAuth()

__all__ = ['jwt_auth', 'JWTAuth']
"@

$content | Out-File -FilePath "src\security\auth.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\security\auth.py" -ForegroundColor Green