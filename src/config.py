import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV = os.getenv('ENV', 'development')
    DEBUG = ENV == 'development'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'dev-encryption-key')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./agent_prospection.db')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/agent.log')
    
    @staticmethod
    def validate_all():
        # Crée les dossiers nécessaires
        Path('logs').mkdir(parents=True, exist_ok=True)
        Path('data').mkdir(parents=True, exist_ok=True)
        Path('data/cache').mkdir(parents=True, exist_ok=True)
        return True

config = Config()
config.validate_all()
