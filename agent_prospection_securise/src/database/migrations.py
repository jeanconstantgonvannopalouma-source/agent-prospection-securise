$content = @"
"""
Module de migrations de base de données
Gère les versions et changements de schéma
"""

from datetime import datetime
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.connection import db
from database.models import Base

logger = logging.getLogger(__name__)

class DatabaseMigrations:
    """Gère les migrations de BD"""
    
    @staticmethod
    def init_database():
        """Initialise la BD (crée toutes les tables)"""
        try:
            logger.info("🔄 Initialisation BD...")
            Base.metadata.create_all(db._engine)
            logger.info("✓ BD initialisée")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur initialisation BD: {e}")
            return False
    
    @staticmethod
    def drop_all():
        """Supprime TOUTES les tables (ATTENTION!)"""
        try:
            logger.warning("⚠️ SUPPRESSION DE TOUTES LES TABLES...")
            Base.metadata.drop_all(db._engine)
            logger.warning("✓ Toutes les tables supprimées")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur suppression: {e}")
            return False
    
    @staticmethod
    def reset_database():
        """Réinitialise complètement la BD"""
        try:
            logger.warning("⚠️ RÉINITIALISATION COMPLÈTE BD...")
            DatabaseMigrations.drop_all()
            DatabaseMigrations.init_database()
            logger.info("✓ BD réinitialisée")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur réinitialisation: {e}")
            return False

migrations = DatabaseMigrations()

__all__ = ['migrations', 'DatabaseMigrations']
"@

$content | Out-File -FilePath "src\database\migrations.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\database\migrations.py" -ForegroundColor Green