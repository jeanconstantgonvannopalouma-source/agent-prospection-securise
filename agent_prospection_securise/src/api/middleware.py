$content = @"
"""
Middleware de sécurité API
Gère l'authentification, rate limiting, CORS, etc.
"""

import logging
from functools import wraps
from typing import Callable, Optional, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config
from security.auth import jwt_auth
from security.rate_limiter import rate_limiter
from security.validation import InputValidator

logger = logging.getLogger(__name__)
validator = InputValidator()

def require_auth(func: Callable) -> Callable:
    """Décorateur pour authentification JWT"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Récupère le token
        token = kwargs.get('token') or (args[0] if args else None)
        
        if not token:
            logger.warning("❌ Aucun token fourni")
            return {'error': 'Token manquant'}, 401
        
        # Vérifie le token
        is_valid, payload, msg = jwt_auth.verify_token(token)
        
        if not is_valid:
            logger.warning(f"❌ Token invalide: {msg}")
            return {'error': msg}, 401
        
        # Ajoute le payload aux kwargs
        kwargs['user'] = payload
        
        return func(*args, **kwargs)
    
    return wrapper

def rate_limit(identifier_key: str = 'email') -> Callable:
    """Décorateur pour rate limiting"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Récupère l'identifiant
            identifier = kwargs.get(identifier_key, 'unknown')
            
            # Vérifie le rate limit
            is_allowed, msg = rate_limiter.is_allowed(identifier)
            
            if not is_allowed:
                logger.warning(f"Rate limit dépassé: {identifier}")
                return {'error': msg}, 429
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def validate_input(schema: type) -> Callable:
    """Décorateur pour validation d'input"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, data: Dict = None, **kwargs):
            if not data:
                return {'error': 'Aucune donnée fournie'}, 400
            
            try:
                # Valide avec Pydantic
                validated = schema(**data)
                kwargs['validated_data'] = validated.dict()
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Erreur validation: {e}")
                return {'error': f'Validation échouée: {str(e)}'}, 400
        
        return wrapper
    return decorator

class SecurityHeaders:
    """Headers de sécurité HTTP"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Retourne les headers de sécurité"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
        }

class CORSMiddleware:
    """Gère CORS de manière sécurisée"""
    
    @staticmethod
    def is_origin_allowed(origin: str) -> bool:
        """Vérifie si l'origine est autorisée"""
        return origin in config.ALLOWED_HOSTS
    
    @staticmethod
    def get_cors_headers(origin: str) -> Dict[str, str]:
        """Retourne les headers CORS"""
        if CORSMiddleware.is_origin_allowed(origin):
            return {
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '3600',
            }
        return {}

__all__ = ['require_auth', 'rate_limit', 'validate_input', 'SecurityHeaders', 'CORSMiddleware']
"@

$content | Out-File -FilePath "src\api\middleware.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\api\middleware.py" -ForegroundColor Green