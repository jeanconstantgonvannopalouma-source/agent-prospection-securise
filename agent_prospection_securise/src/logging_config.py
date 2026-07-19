$content = @"
"""
Configuration avancée du logging
Gère les logs avec rotation, niveau dynamique, etc.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
import json

# Import config
from config import config

class ColoredFormatter(logging.Formatter):
    """Formatter avec couleurs pour console"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Vert
        'WARNING': '\033[33m',    # Jaune
        'ERROR': '\033[31m',      # Rouge
        'CRITICAL': '\033[41m'    # Rouge fond
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f'{log_color}{record.levelname}{self.RESET}'
        return super().format(record)

class SecureJsonFormatter(logging.Formatter):
    """Formatter JSON sécurisé pour fichier"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Ajoute l'exception si présente
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)

def setup_logging(logger_name: str = None) -> logging.Logger:
    """Configure le système de logging complet"""
    
    logger = logging.getLogger(logger_name or __name__)
    
    # Vérifie si déjà configuré
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # ===== FORMATTER CONSOLE =====
    console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_formatter = ColoredFormatter(
        console_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ===== HANDLER CONSOLE =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(console_handler)
    
    # ===== HANDLER FICHIER AVEC ROTATION =====
    try:
        log_file = Path(config.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Formatter JSON pour fichier
        file_formatter = SecureJsonFormatter()
        
        # Handler avec rotation
        file_handler = logging.handlers.RotatingFileHandler(
            str(log_file),
            maxBytes=config.MAX_LOG_SIZE,
            backupCount=config.BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        file_handler.setFormatter(file_formatter)
        
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Erreur création handler fichier: {e}")
    
    # ===== HANDLER SENTRY (si configuré) =====
    if config.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            sentry_sdk.init(
                dsn=config.SENTRY_DSN,
                traces_sample_rate=0.1,
                integrations=[
                    LoggingIntegration(
                        level=logging.INFO,
                        event_level=logging.ERROR
                    )
                ],
                environment=config.ENV
            )
            logger.info("✓ Sentry intégré")
        except Exception as e:
            logger.warning(f"Sentry non disponible: {e}")
    
    return logger

# Initialise le logger global
logger = setup_logging('agent_prospection')

__all__ = ['setup_logging', 'logger', 'ColoredFormatter', 'SecureJsonFormatter']
"@

$content | Out-File -FilePath "src\logging_config.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\logging_config.py" -ForegroundColor Green