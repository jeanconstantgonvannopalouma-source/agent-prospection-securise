$content = @"
"""
Configuration centralisée et sécurisée
Gère tous les paramètres de l'application
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging
from typing import Optional

# ============================================================
# CHEMINS DE BASE
# ============================================================

BASE_DIR = Path(__file__).parent.parent
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Charge les variables d'environnement
dotenv_path = BASE_DIR.parent / '.env'
load_dotenv(dotenv_path)

# ============================================================
# CLASSE CONFIGURATION PRINCIPALE
# ============================================================

class Config:
    """Configuration centrale - ULTRA SÉCURISÉE"""
    
    # ========== ENVIRONNEMENT ==========
    ENV = os.getenv('ENV', 'development').lower()
    DEBUG = ENV == 'development'
    TESTING = ENV == 'testing'
    
    if ENV not in ['development', 'staging', 'production']:
        raise ValueError(f"❌ ENV invalide: {ENV}. Doit être: development, staging, production")
    
    # ========== CLÉS SECRÈTES ==========
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("❌ ERREUR: SECRET_KEY manquante dans .env")
    
    if len(SECRET_KEY) < 32:
        raise ValueError(f"❌ ERREUR: SECRET_KEY trop courte ({len(SECRET_KEY)} chars). Min: 32")
    
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    if not ENCRYPTION_KEY:
        raise ValueError("❌ ERREUR: ENCRYPTION_KEY manquante dans .env")
    
    # ========== BASE DE DONNÉES ==========
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("❌ ERREUR: DATABASE_URL manquante dans .env")
    
    # Valide le format DATABASE_URL
    if not any(proto in DATABASE_URL for proto in ['sqlite:', 'postgresql:', 'mysql:', 'mariadb:']):
        raise ValueError(f"❌ ERREUR: DATABASE_URL invalide: {DATABASE_URL}")
    
    # ========== API OPENAI ==========
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_MAX_RETRIES = int(os.getenv('OPENAI_MAX_RETRIES', 3))
    OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', 30))
    
    # ========== SÉCURITÉ - RATE LIMITING ==========
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', 1000))
    
    if RATE_LIMIT_PER_MINUTE <= 0 or RATE_LIMIT_PER_HOUR <= 0:
        raise ValueError("❌ ERREUR: Rate limits doivent être > 0")
    
    if RATE_LIMIT_PER_HOUR < RATE_LIMIT_PER_MINUTE:
        raise ValueError("❌ ERREUR: Rate limit heure doit être >= minute")
    
    # ========== JWT ==========
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', 24))
    
    # ========== LOGGING ==========
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.getenv('LOG_FILE', 'logs\\agent.log')
    MAX_LOG_SIZE = int(os.getenv('MAX_LOG_SIZE', 10485760))  # 10MB
    BACKUP_COUNT = int(os.getenv('BACKUP_COUNT', 5))
    
    # ========== SÉCURITÉ - CORS ==========
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0'
    ]
    
    # ========== SENTRY (ERROR TRACKING) ==========
    SENTRY_DSN = os.getenv('SENTRY_DSN', None)
    
    # ========== VALIDATION & SÉCURITÉ ==========
    MAX_INPUT_LENGTH = int(os.getenv('MAX_INPUT_LENGTH', 10000))
    MAX_EMAIL_LENGTH = 255
    MAX_PHONE_LENGTH = 20
    
    # Validations de sécurité
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # ========== TIMEOUTS ==========
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    DATABASE_TIMEOUT = int(os.getenv('DATABASE_TIMEOUT', 20))
    
    # ========== PAGINATION ==========
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 50))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 1000))
    
    @classmethod
    def validate_all(cls) -> bool:
        """Valide TOUTE la configuration"""
        try:
            # Crée les répertoires nécessaires
            log_dir = Path(cls.LOG_FILE).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            data_dir = BASE_DIR.parent / 'data'
            data_dir.mkdir(parents=True, exist_ok=True)
            
            cache_dir = BASE_DIR.parent / 'data' / 'cache'
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            raise ValueError(f"❌ ERREUR validation config: {e}")
    
    @classmethod
    def display_config(cls) -> None:
        """Affiche la configuration courante (sans secrets)"""
        print("\n" + "="*60)
        print("CONFIGURATION DE L'APPLICATION")
        print("="*60)
        print(f"Environnement: {cls.ENV}")
        print(f"Debug: {cls.DEBUG}")
        print(f"Base de données: {cls.DATABASE_URL[:50]}...")
        print(f"OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"Rate Limit/min: {cls.RATE_LIMIT_PER_MINUTE}")
        print(f"Rate Limit/h: {cls.RATE_LIMIT_PER_HOUR}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print(f"Log File: {cls.LOG_FILE}")
        print("="*60 + "\n")

# ============================================================
# CLASSES DE CONFIGURATION SPÉCIFIQUES
# ============================================================

class DevelopmentConfig(Config):
    """Configuration pour développement"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Configuration pour tests"""
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configuration pour production"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'

# ============================================================
# SÉLECTION DE LA CONFIGURATION
# ============================================================

config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

config = config_map.get(Config.ENV, Config)

# Valide la configuration au démarrage
try:
    config.validate_all()
    # config.display_config()
except Exception as e:
    print(f"❌ ERREUR FATALE: {e}")
    sys.exit(1)

__all__ = ['config', 'Config', 'DevelopmentConfig', 'TestingConfig', 'ProductionConfig']
"@

$content | Out-File -FilePath "src\config.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\config.py" -ForegroundColor Green