"""Authentification JWT"""
import jwt
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class JWTAuth:
    def __init__(self, secret: str):
        self.secret = secret
        self.algorithm = 'HS256'
        self.token_expiry_hours = 24
    
    def generate_token(self, user_id: str, email: str, roles: list = None) -> str:
        if not user_id or not email:
            raise ValueError("user_id et email requis")
        
        try:
            payload = {
                'user_id': user_id,
                'email': email,
                'roles': roles or ['user'],
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
            }
            
            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            logger.info(f"Token généré pour {email}")
            return token
        except Exception as e:
            logger.error(f"Erreur génération token: {e}")
            raise
    
    def verify_token(self, token: str) -> tuple:
        if not token or not isinstance(token, str):
            return False, None, "Token manquant"
        
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            logger.info(f"Token vérifié pour {payload.get('email')}")
            return True, payload, "Token valide"
        except jwt.ExpiredSignatureError:
            return False, None, "Token expiré"
        except jwt.InvalidTokenError as e:
            return False, None, f"Token invalide: {str(e)}"
        except Exception as e:
            logger.error(f"Erreur vérification: {e}")
            return False, None, str(e)

jwt_auth = None

def init_jwt(secret):
    global jwt_auth
    jwt_auth = JWTAuth(secret)
    return jwt_auth
