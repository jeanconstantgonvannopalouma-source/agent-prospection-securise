$content = @"
"""
Repository Pattern - Data Access Layer
Isolate all database operations
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, asc
from datetime import datetime, timedelta
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.models import (
    Prospect, ProspectStatus, Interaction, InteractionType,
    Message, MessageStatus, Objection, AuditLog
)
from security.validation import InputValidator
from security.sanitizer import DataSanitizer

logger = logging.getLogger(__name__)
validator = InputValidator()
sanitizer = DataSanitizer()

class ProspectRepository:
    """Repository pour les prospects"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, prospect_data: Dict[str, Any]) -> Optional[Prospect]:
        """
        Crée un prospect avec validation complète
        
        Args:
            prospect_data: Dictionnaire des données
            
        Returns:
            Prospect créé ou None
        """
        # Valide les données
        is_valid, errors = validator.validate_prospect_data(prospect_data)
        if not is_valid:
            logger.error(f"❌ Données prospect invalides: {errors}")
            raise ValueError(f"Erreurs validation: {errors}")
        
        try:
            # Vérifie l'existence
            existing = self.get_by_email(prospect_data['email'])
            if existing:
                logger.warning(f"⚠️ Prospect déjà existe: {prospect_data['email']}")
                return existing
            
            # Crée le prospect
            prospect = Prospect(
                first_name=sanitizer.sanitize_string(prospect_data['first_name']),
                last_name=sanitizer.sanitize_string(prospect_data.get('last_name', '')),
                email=sanitizer.sanitize_email(prospect_data['email']),
                phone=sanitizer.sanitize_phone(prospect_data.get('phone', '')) if prospect_data.get('phone') else None,
                company_name=sanitizer.sanitize_string(prospect_data['company']),
                job_title=sanitizer.sanitize_string(prospect_data.get('job_title', '')),
                industry=prospect_data.get('industry'),
                country=prospect_data.get('country'),
                status=ProspectStatus.NEW,
                source=prospect_data.get('source', 'manual'),
                created_at=datetime.utcnow()
            )
            
            self.session.add(prospect)
            self.session.flush()  # Obtient l'ID
            self.session.commit()
            
            logger.info(f"✓ Prospect créé: {prospect.email} (ID: {prospect.id})")
            return prospect
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erreur création prospect: {e}")
            raise
    
    def get_by_email(self, email: str) -> Optional[Prospect]:
        """Récupère un prospect par email"""
        try:
            return self.session.query(Prospect).filter(
                Prospect.email == email.lower()
            ).first()
        except Exception as e:
            logger.error(f"❌ Erreur requête par email: {e}")
            raise
    
    def get_by_id(self, prospect_id: int) -> Optional[Prospect]:
        """Récupère un prospect par ID"""
        try:
            return self.session.query(Prospect).filter(
                Prospect.id == prospect_id
            ).first()
        except Exception as e:
            logger.error(f"❌ Erreur requête par ID: {e}")
            raise
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Prospect]:
        """Récupère tous les prospects avec pagination"""
        try:
            return self.session.query(Prospect).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"❌ Erreur requête all: {e}")
            raise
    
    def find_by_status(self, status: ProspectStatus, limit: int = 100) -> List[Prospect]:
        """Trouve prospects par statut"""
        try:
            return self.session.query(Prospect).filter(
                Prospect.status == status
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"❌ Erreur filtrage statut: {e}")
            raise
    
    def find_by_company(self, company_name: str, limit: int = 100) -> List[Prospect]:
        """Trouve prospects par entreprise"""
        try:
            return self.session.query(Prospect).filter(
                Prospect.company_name.ilike(f'%{company_name}%')
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"❌ Erreur filtrage entreprise: {e}")
            raise
    
    def find_high_quality(self, min_score: int = 70, limit: int = 100) -> List[Prospect]:
        """Trouve prospects haute qualité"""
        try:
            return self.session.query(Prospect).filter(
                and_(
                    Prospect.qualification_score >= min_score,
                    Prospect.status == ProspectStatus.NEW
                )
            ).order_by(desc(Prospect.qualification_score)).limit(limit).all()
        except Exception as e:
            logger.error(f"❌ Erreur recherche haute qualité: {e}")
            raise
    
    def find_by_country(self, country: str, limit: int = 100) -> List[Prospect]:
        """Trouve prospects par pays"""
        try:
            return self.session.query(Prospect).filter(
                Prospect.country == country.upper()
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"❌ Erreur filtrage pays: {e}")
            raise
    
    def find_decision_makers(self, limit: int = 100) -> List[Prospect]:
        """Trouve les décideurs"""
        try:
            return self.session.query(Prospect).filter(
                Prospect.is_decision_maker == True
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"❌ Erreur recherche décideurs: {e}")
            raise
    
    def update_status(self, prospect_id: int, new_status: ProspectStatus) -> bool:
        """Met à jour le statut"""
        try:
            prospect = self.get_by_id(prospect_id)
            if not prospect:
                logger.warning(f"⚠️ Prospect non trouvé: {prospect_id}")
                return False
            
            old_status = prospect.status
            prospect.status = new_status
            prospect.updated_at = datetime.utcnow()
            
            self.session.commit()
            logger.info(f"✓ Statut mise à jour: {prospect.email} ({old_status.value} → {new_status.value})")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erreur mise à jour statut: {e}")
            raise
    
    def update_scores(
        self,
        prospect_id: int,
        qualification_score: int,
        conversion_probability: float,
        engagement_score: int = None
    ) -> bool:
        """Met à jour les scores IA"""
        try:
            prospect = self.get_by_id(prospect_id)
            if not prospect:
                return False
            
            # Valide les scores
            if not (0 <= qualification_score <= 100):
                raise ValueError("Qualification score: 0-100")
            if not (0.0 <= conversion_probability <= 1.0):
                raise ValueError("Conversion probability: 0.0-1.0")
            
            prospect.qualification_score = qualification_score
            prospect.conversion_probability = conversion_probability
            if engagement_score is not None:
                prospect.engagement_score = engagement_score
            prospect.updated_at = datetime.utcnow()
            
            self.session.commit()
            logger.debug(f"✓ Scores mis à jour: {prospect.email}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erreur mise à jour scores: {e}")
            raise
    
    def update_contact_info(self, prospect_id: int, **kwargs) -> bool:
        """Met à jour les infos de contact"""
        try:
            prospect = self.get_by_id(prospect_id)
            if not prospect:
                return False
            
            allowed_fields = {
                'phone': 'phone',
                'job_title': 'job_title',
                'department': 'department',
                'industry': 'industry',
                'company_size': 'company_size',
            }
            
            for key, field in allowed_fields.items():
                if key in kwargs:
                    setattr(prospect, field, sanitizer.sanitize_string(str(kwargs[key])))
            
            prospect.updated_at = datetime.utcnow()
            self.session.commit()
            logger.info(f"✓ Infos mise à jour: {prospect.email}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erreur mise à jour infos: {e}")
            raise
    
    def increment_interaction_count(self, prospect_id: int) -> bool:
        """Incrémente le compteur d'interactions"""
        try:
            prospect = self.get_by_id(prospect_id)
            if not prospect:
                return False
            
            prospect.total_interactions += 1
            prospect.last_contacted = datetime.utcnow()
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erreur incrémentation: {e}")
            raise
    
    def delete(self, prospect_id: int) -> bool:
        """Supprime un prospect"""
        try:
            prospect = self.get_by_id(prospect_id)
            if not prospect:
                return False
            
            self.session.delete(prospect)
            self.session.commit()
            logger.info(f"✓ Prospect supprimé: {prospect_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erreur suppression: {e}")
            raise
    
    def count(self) -> int:
        """Compte le nombre total de prospects"""
        try:
            return self.session.query(func.count(Prospect.id)).scalar()
        except Exception as e:
            logger.error(f"❌ Erreur count: {e}")
            raise
    
    def count_by_status(self, status: ProspectStatus) -> int:
        """Compte prospects par statut"""
        try:
            return self.session.query(func.count(Prospect.id)).filter(
                Prospect.status == status
            ).scalar()
        except Exception as e:
            logger.error(f"❌ Erreur count par statut: {e}")
            raise

class MessageRepository:
    """Repository pour les messages"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        prospect_id: int,
        subject: str,
        body: str,
        channel: str = 'email',
        status: MessageStatus = MessageStatus.DRAFT
    ) -> Optional[Message]:
        """Crée un message"""
        try:
            message = Message(
                prospect_id=prospect_id,
                subject=sanitizer.sanitize_string(subject, max_length=255),
                body=sanitizer.sanitize_string(body),
                channel=channel,
                status=status,
                generated_by_ai=True,
                ai_model='gpt-4'
            )
            
            self.session.add(message)
            self.session.commit()
            logger.info(f"✓ Message créé (ID: {message.id})")
            return message
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erreur création message: {e}")
            raise
    
    def get_by_id(self, message_id: int) -> Optional[Message]:
        """Récupère un message"""
        try:
            return self.session.query(Message).filter(
                Message.id == message_id
            ).first()
        except Exception as e:
            logger.error(f"❌ Erreur récupération message: {e}")
            raise
    
    def get_by_prospect(self, prospect_id: int, limit: int = 50) -> List[Message]:
        """Récupère les messages d'un prospect"""
        try:
            return self.session.query(Message).filter(
                Message.prospect_id == prospect_id
            ).order_by(desc(Message.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"❌ Erreur requête messages: {e}")
            raise
    
    def update_status(self, message_id: int, new_status: MessageStatus) -> bool:
        """Met à jour le statut d'un message"""
        try:
            message = self.get_by_id(message_id)
            if not message:
                return False
            
            message.status = new_status
            if new_status == MessageStatus.SENT:
                message.sent_at = datetime.utcnow()
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erreur mise à jour message: {e}")
            raise

class InteractionRepository:
    """Repository pour les interactions"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        prospect_id: int,
        interaction_type: InteractionType,
        subject: str = None,
        content: str = None
    ) -> Optional[Interaction]:
        """Crée une interaction"""
        try:
            interaction = Interaction(
                prospect_id=prospect_id,
                type=interaction_type,
                subject=sanitizer.sanitize_string(subject) if subject else None,
                content=sanitizer.sanitize_string(content) if content else None,
                created_at=datetime.utcnow()
            )
            
            self.session.add(interaction)
            self.session.commit()
            logger.info(f"✓ Interaction créée (ID: {interaction.id})")
            return interaction
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erreur création interaction: {e}")
            raise
    
    def get_by_prospect(self, prospect_id: int, limit: int = 100) -> List[Interaction]:
        """Récupère les interactions d'un prospect"""
        try:
            return self.session.query(Interaction).filter(
                Interaction.prospect_id == prospect_id
            ).order_by(desc(Interaction.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"❌ Erreur requête interactions: {e}")
            raise

__all__ = [
    'ProspectRepository',
    'MessageRepository',
    'InteractionRepository'
]
"@

$content | Out-File -FilePath "src\database\repositories.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\database\repositories.py" -ForegroundColor Green