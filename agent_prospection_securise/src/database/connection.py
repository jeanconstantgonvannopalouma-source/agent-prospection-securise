$content = @"
"""
Connexion sécurisée à la base de données
Gère le pool de connexions, retries, etc.
"""

from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool, StaticPool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import sys
from pathlib import Path
import logging
from typing import Optional, Callable, Any
import time

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config
from database.models import Base

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Gestion sécurisée et robuste de la connexion BD
    Singleton pattern avec retry automatique
    """
    
    _instance = None
    _lock = __import__('threading').Lock()
    
    _engine = None
    _session_local = None
    _connection_attempts = 0
    _max_connection_attempts = 3
    
    def __new__(cls):
        """Singleton pattern thread-safe"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialise la connexion BD de manière sécurisée"""
        try:
            logger.info(f"🔌 Initialisation connexion BD: {config.DATABASE_URL[:50]}...")
            
            # ===== DÉTECTE LE TYPE DE BD =====
            db_type = self._detect_db_type()
            
            # ===== CONFIGURE L'ENGINE =====
            if db_type == 'sqlite':
                self._engine = self._create_sqlite_engine()
            elif db_type == 'postgresql':
                self._engine = self._create_postgresql_engine()
            else:
                raise ValueError(f"❌ Type BD non supporté: {db_type}")
            
            # ===== CONFIGURE LES ÉVÉNEMENTS =====
            self._setup_event_handlers()
            
            # ===== CRÉE LES TABLES =====
            Base.metadata.create_all(self._engine)
            logger.info("✓ Tables créées/vérifiées")
            
            # ===== CRÉE LA SESSION FACTORY =====
            self._session_local = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
                expire_on_commit=False
            )
            
            # ===== TEST DE CONNEXION =====
            self._test_connection()
            
            logger.info("✓✓✓ Connexion BD sécurisée établie!")
            
        except Exception as e:
            logger.error(f"❌ ERREUR FATALE connexion BD: {e}")
            raise
    
    def _detect_db_type(self) -> str:
        """Détecte le type de BD"""
        if 'sqlite' in config.DATABASE_URL:
            return 'sqlite'
        elif 'postgresql' in config.DATABASE_URL:
            return 'postgresql'
        else:
            raise ValueError(f"❌ BD non supportée: {config.DATABASE_URL}")
    
    def _create_sqlite_engine(self):
        """Crée un engine SQLite"""
        return create_engine(
            config.DATABASE_URL,
            connect_args={
                'timeout': config.DATABASE_TIMEOUT,
                'check_same_thread': False,
            },
            poolclass=StaticPool,
            echo=config.DEBUG,
            echo_pool=config.DEBUG,
        )
    
    def _create_postgresql_engine(self):
        """Crée un engine PostgreSQL"""
        return create_engine(
            config.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,  # Recycle après 1h
            pool_pre_ping=True,  # Vérifie connexion avant utilisation
            connect_args={
                'timeout': config.DATABASE_TIMEOUT,
                'connect_timeout': config.DATABASE_TIMEOUT,
            },
            echo=config.DEBUG,
            echo_pool=config.DEBUG,
        )
    
    def _setup_event_handlers(self):
        """Configure les event handlers de sécurité"""
        
        @event.listens_for(self._engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            """Configure pragma SQLite"""
            if 'sqlite' in config.DATABASE_URL:
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()
                logger.debug("✓ SQLite pragmas configurés")
        
        @event.listens_for(self._engine, "engine_disposed")
        def receive_engine_disposed(engine):
            """Événement lors de la réinitialisation du moteur"""
            logger.warning("⚠️ Moteur BD réinitialisé")
        
        @event.listens_for(self._engine, "handle_error")
        def receive_handle_error(exception, context):
            """Gère les erreurs de connexion"""
            logger.error(f"❌ Erreur BD: {exception}")
            return None
    
    def _test_connection(self):
        """Teste la connexion BD"""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Test de connexion réussi")
        except Exception as e:
            logger.error(f"❌ Échec test connexion: {e}")
            raise
    
    def get_session(self) -> Session:
        """
        Retourne une nouvelle session BD
        
        Returns:
            Session SQLAlchemy
            
        Raises:
            RuntimeError: Si impossible créer session
        """
        if not self._session_local:
            raise RuntimeError("❌ Session factory non initialisée")
        
        try:
            session = self._session_local()
            logger.debug(f"✓ Session créée: {id(session)}")
            return session
        except Exception as e:
            logger.error(f"❌ Erreur création session: {e}")
            raise
    
    def close_session(self, session: Session) -> None:
        """
        Ferme proprement une session
        
        Args:
            session: Session à fermer
        """
        if not session:
            return
        
        try:
            session.commit()
            logger.debug(f"✓ Session committée: {id(session)}")
        except Exception as e:
            logger.error(f"❌ Erreur commit: {e}")
            session.rollback()
        finally:
            try:
                session.close()
                logger.debug(f"✓ Session fermée: {id(session)}")
            except Exception as e:
                logger.error(f"❌ Erreur fermeture session: {e}")
    
    def execute_with_retry(
        self,
        func: Callable,
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> Any:
        """
        Exécute une fonction avec retry automatique
        Utilise exponential backoff
        
        Args:
            func: Fonction à exécuter (prend session en paramètre)
            max_retries: Nombre max de tentatives
            backoff_factor: Facteur d'augmentation du délai
            
        Returns:
            Résultat de la fonction
            
        Raises:
            Exception: Après tous les retries échoués
        """
        for attempt in range(max_retries):
            session = None
            try:
                session = self.get_session()
                result = func(session)
                self.close_session(session)
                return result
                
            except OperationalError as e:
                logger.warning(f"⚠️ Erreur opérationnel (tentative {attempt + 1}/{max_retries}): {e}")
                if session:
                    self.close_session(session)
                
                if attempt < max_retries - 1:
                    delay = backoff_factor ** attempt
                    logger.info(f"Retry dans {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"❌ Tous les retries échoués")
                    raise
                    
            except Exception as e:
                logger.error(f"❌ Erreur non-opérationnel: {e}")
                if session:
                    self.close_session(session)
                raise
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion BD"""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Health check: BD opérationnelle")
            return True
        except Exception as e:
            logger.error(f"❌ Health check échoué: {e}")
            return False
    
    def reset(self):
        """Réinitialise la connexion BD"""
        logger.warning("⚠️ Réinitialisation de la BD...")
        if self._engine:
            self._engine.dispose()
        self._initialize()

# Instance globale singleton
db = DatabaseConnection()

__all__ = ['db', 'DatabaseConnection']
"@

$content | Out-File -FilePath "src\database\connection.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\database\connection.py" -ForegroundColor Green