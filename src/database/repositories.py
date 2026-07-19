"""Data Access Layer - Repositories"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
import logging

from database.models import Prospect, ProspectStatus, Message, Interaction
from security.validation import validator

logger = logging.getLogger(__name__)

# Classe de nettoyage intégrée
class DataSanitizer:
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        if not text:
            return ""
        return text[:max_length].strip()

sanitizer = DataSanitizer()

class ProspectRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, prospect_data: dict) -> Prospect:
        is_valid, errors = validator.validate_prospect_data(prospect_data)
        if not is_valid:
            raise ValueError(f"Erreurs: {errors}")
        
        try:
            existing = self.get_by_email(prospect_data['email'])
            if existing:
                logger.warning(f"Prospect existe: {prospect_data['email']}")
                return existing
            
            prospect = Prospect(
                first_name=sanitizer.sanitize_string(prospect_data['first_name']),
                last_name=sanitizer.sanitize_string(prospect_data.get('last_name', '')),
                email=prospect_data['email'].lower(),
                phone=prospect_data.get('phone'),
                company_name=sanitizer.sanitize_string(prospect_data['company']),
                job_title=sanitizer.sanitize_string(prospect_data.get('job_title', '')),
                industry=prospect_data.get('industry'),
                country=prospect_data.get('country'),
                status=ProspectStatus.NEW
            )
            
            self.session.add(prospect)
            self.session.flush()
            self.session.commit()
            
            logger.info(f"✓ Prospect créé: {prospect.email}")
            return prospect
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur création: {e}")
            raise
    
    def get_by_email(self, email: str) -> Prospect:
        try:
            return self.session.query(Prospect).filter(
                Prospect.email == email.lower()
            ).first()
        except Exception as e:
            logger.error(f"Erreur requête: {e}")
            raise
    
    def get_by_id(self, prospect_id: int) -> Prospect:
        try:
            return self.session.query(Prospect).filter(
                Prospect.id == prospect_id
            ).first()
        except Exception as e:
            logger.error(f"Erreur requête: {e}")
            raise
    
    def get_all(self, limit: int = 100) -> list:
        try:
            return self.session.query(Prospect).limit(limit).all()
        except Exception as e:
            logger.error(f"Erreur requête: {e}")
            raise
    
    def find_by_status(self, status: ProspectStatus) -> list:
        try:
            return self.session.query(Prospect).filter(
                Prospect.status == status
            ).all()
        except Exception as e:
            logger.error(f"Erreur filtrage: {e}")
            raise
    
    def update_status(self, prospect_id: int, new_status: ProspectStatus) -> bool:
        try:
            prospect = self.get_by_id(prospect_id)
            if not prospect:
                return False
            
            prospect.status = new_status
            prospect.updated_at = datetime.utcnow()
            self.session.commit()
            
            logger.info(f"✓ Statut updaté: {prospect.email}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur update: {e}")
            raise
    
    def update_scores(self, prospect_id: int, qual_score: int, conv_prob: float) -> bool:
        try:
            prospect = self.get_by_id(prospect_id)
            if not prospect:
                return False
            
            prospect.qualification_score = max(0, min(100, qual_score))
            prospect.conversion_probability = max(0.0, min(1.0, conv_prob))
            prospect.updated_at = datetime.utcnow()
            self.session.commit()
            
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur scores: {e}")
            raise
    
    def count(self) -> int:
        try:
            return self.session.query(Prospect).count()
        except Exception as e:
            logger.error(f"Erreur count: {e}")
            raise
    
    def count_by_status(self, status: ProspectStatus) -> int:
        try:
            return self.session.query(Prospect).filter(
                Prospect.status == status
            ).count()
        except Exception as e:
            logger.error(f"Erreur count: {e}")
            raise

class MessageRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, prospect_id: int, subject: str, body: str, channel: str = 'email') -> Message:
        try:
            message = Message(
                prospect_id=prospect_id,
                subject=sanitizer.sanitize_string(subject, 255),
                body=sanitizer.sanitize_string(body),
                channel=channel,
                status='draft'
            )
            
            self.session.add(message)
            self.session.commit()
            
            return message
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur création message: {e}")
            raise
    
    def get_by_id(self, message_id: int) -> Message:
        try:
            return self.session.query(Message).filter(
                Message.id == message_id
            ).first()
        except Exception as e:
            logger.error(f"Erreur requête: {e}")
            raise
