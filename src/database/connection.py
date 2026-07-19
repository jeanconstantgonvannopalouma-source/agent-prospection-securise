"""Connexion sécurisée à la base de données"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import logging
import sys
from pathlib import Path

from database.models import Base

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    
    def __new__(cls, database_url):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(database_url)
        return cls._instance
    
    def _initialize(self, database_url):
        try:
            logger.info(f"BD: {database_url[:50]}")
            
            if 'sqlite' in database_url:
                self.engine = create_engine(
                    database_url,
                    connect_args={'check_same_thread': False},
                    echo=False
                )
            else:
                self.engine = create_engine(
                    database_url,
                    pool_size=10,
                    max_overflow=20,
                    echo=False
                )
            
            Base.metadata.create_all(self.engine)
            logger.info("Tables OK")
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("BD init OK")
            
        except Exception as e:
            logger.error(f"BD error: {e}")
            raise
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Commit error: {e}")
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """Vérifie la santé de la BD"""
        try:
            session = self.get_session()
            session.execute(text("SELECT 1"))
            self.close_session(session)
            return True
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False

# Instance globale
db = None

def init_db(database_url):
    global db
    db = DatabaseConnection(database_url)
    return db
