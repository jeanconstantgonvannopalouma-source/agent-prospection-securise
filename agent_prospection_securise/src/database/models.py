$content = @"
"""
Modèles de base de données SQLAlchemy
Définit TOUTES les tables et relations
"""

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, 
    DateTime, Boolean, Text, ForeignKey, UniqueConstraint,
    Index, Enum, JSON, LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import logging
from typing import Optional

logger = logging.getLogger(__name__)
Base = declarative_base()

# ============================================================
# ENUMS
# ============================================================

class ProspectStatus(enum.Enum):
    """Statuts possibles d'un prospect"""
    NEW = "nouveau"
    CONTACTED = "contacté"
    QUALIFIED = "qualifié"
    DEMOING = "en_présentation"
    NEGOTIATING = "en_négociation"
    WON = "remporté"
    LOST = "perdu"
    UNQUALIFIED = "non_qualifié"
    ARCHIVED = "archivé"

class InteractionType(enum.Enum):
    """Types d'interactions"""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "téléphone"
    DEMO = "démonstration"
    MEETING = "réunion"
    CALL = "appel"
    OTHER = "autre"

class MessageStatus(enum.Enum):
    """Statuts des messages"""
    DRAFT = "brouillon"
    SCHEDULED = "planifié"
    SENDING = "envoi"
    SENT = "envoyé"
    FAILED = "échoué"
    BOUNCED = "rejeté"

class SentimentScore(enum.Enum):
    """Scores de sentiment"""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2

# ============================================================
# MODÈLE: PROSPECT
# ============================================================

class Prospect(Base):
    """
    Modèle pour stocker les prospects
    ULTRA robuste avec validations et indexes
    """
    __tablename__ = 'prospects'
    
    # ===== CLÉS PRIMAIRES & IDENTIFICATION =====
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), unique=True, nullable=True, index=True)
    
    # ===== INFORMATIONS PERSONNELLES =====
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True, index=True)
    
    # ===== INFORMATIONS ENTREPRISE =====
    company_name = Column(String(255), nullable=False, index=True)
    company_domain = Column(String(255), nullable=True)
    company_size = Column(String(50), nullable=True)  # "10-50", "50-200", etc.
    industry = Column(String(100), nullable=True, index=True)
    
    # ===== POSITION & DÉCISION =====
    job_title = Column(String(150), nullable=False, index=True)
    department = Column(String(100), nullable=True)
    is_decision_maker = Column(Boolean, default=False, index=True)
    
    # ===== BUDGET & STATUT =====
    estimated_budget = Column(Float, nullable=True)
    status = Column(Enum(ProspectStatus), default=ProspectStatus.NEW, index=True)
    
    # ===== SCORING IA =====
    qualification_score = Column(Integer, default=0, index=True)  # 0-100
    conversion_probability = Column(Float, default=0.0)  # 0.0-1.0
    engagement_score = Column(Integer, default=0)  # 0-100
    last_engagement_score = Column(Integer, default=0)
    
    # ===== LOCALISATION =====
    country = Column(String(2), nullable=True, index=True)  # Code ISO
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    # ===== SOURCE & TRACKING =====
    source = Column(String(50), default="manual", index=True)  # linkedin, google, manual, etc.
    source_data = Column(JSON, nullable=True)  # Données enrichies JSON
    
    # ===== HISTORIQUE CONTACT =====
    first_contacted = Column(DateTime, nullable=True, index=True)
    last_contacted = Column(DateTime, nullable=True, index=True)
    total_interactions = Column(Integer, default=0)
    
    # ===== NOTES & TAGS =====
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Liste de tags
    custom_fields = Column(JSON, nullable=True)  # Champs personnalisés
    
    # ===== TIMESTAMPS =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # ===== RELATIONS =====
    interactions = relationship(
        "Interaction",
        back_populates="prospect",
        cascade="all, delete-orphan",
        lazy="select"
    )
    messages = relationship(
        "Message",
        back_populates="prospect",
        cascade="all, delete-orphan",
        lazy="select"
    )
    objections = relationship(
        "Objection",
        back_populates="prospect",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # ===== INDEXES =====
    __table_args__ = (
        UniqueConstraint('email', name='uq_prospect_email'),
        Index('idx_company_country', 'company_name', 'country'),
        Index('idx_status_score', 'status', 'qualification_score'),
        Index('idx_created_score', 'created_at', 'qualification_score'),
        Index('idx_decision_maker', 'is_decision_maker', 'status'),
        Index('idx_last_contacted', 'last_contacted'),
    )
    
    def __repr__(self):
        return f"<Prospect {self.first_name} {self.last_name} ({self.email})>"
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'status': self.status.value if self.status else None,
            'qualification_score': self.qualification_score,
            'conversion_probability': self.conversion_probability,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

# ============================================================
# MODÈLE: INTERACTION
# ============================================================

class Interaction(Base):
    """Historique des interactions avec les prospects"""
    __tablename__ = 'interactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False, index=True)
    
    # Type & contenu
    type = Column(Enum(InteractionType), nullable=False, index=True)
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    
    # Réponse
    response_received = Column(Boolean, default=False, index=True)
    response_content = Column(Text, nullable=True)
    response_time_hours = Column(Integer, nullable=True)
    response_at = Column(DateTime, nullable=True)
    
    # Engagement
    email_opened = Column(Boolean, default=False)
    email_opened_at = Column(DateTime, nullable=True)
    email_clicked = Column(Boolean, default=False)
    email_click_count = Column(Integer, default=0)
    
    # Scoring
    sentiment_score = Column(Enum(SentimentScore), nullable=True)
    engagement_score = Column(Integer, nullable=True)  # 0-100
    
    # Résultat
    result = Column(String(50), nullable=True, index=True)
    next_action = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relation
    prospect = relationship("Prospect", back_populates="interactions")
    
    __table_args__ = (
        Index('idx_prospect_type', 'prospect_id', 'type'),
        Index('idx_created_type', 'created_at', 'type'),
    )

# ============================================================
# MODÈLE: MESSAGE
# ============================================================

class Message(Base):
    """Messages envoyés aux prospects"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False, index=True)
    
    # Contenu
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    personalization_level = Column(Integer, default=0)  # 0-100
    
    # Méta
    channel = Column(String(50), nullable=False, index=True)  # email, linkedin, sms
    status = Column(Enum(MessageStatus), default=MessageStatus.DRAFT, index=True)
    
    # Timing
    scheduled_at = Column(DateTime, nullable=True, index=True)
    sent_at = Column(DateTime, nullable=True, index=True)
    failed_reason = Column(Text, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Performance
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    unsubscribe = Column(Boolean, default=False)
    
    # IA
    generated_by_ai = Column(Boolean, default=True)
    ai_model = Column(String(50), nullable=True)  # gpt-4, gpt-3.5-turbo
    ai_version = Column(String(20), nullable=True)
    
    # Metadata
    send_delay_seconds = Column(Integer, nullable=True)
    a_b_test_group = Column(String(50), nullable=True)
    
    # Relation
    prospect = relationship("Prospect", back_populates="messages")
    
    __table_args__ = (
        Index('idx_prospect_status', 'prospect_id', 'status'),
        Index('idx_sent_at', 'sent_at'),
        Index('idx_scheduled_at', 'scheduled_at'),
    )

# ============================================================
# MODÈLE: OBJECTION
# ============================================================

class Objection(Base):
    """Objections rencontrées"""
    __tablename__ = 'objections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False, index=True)
    
    # Objection
    text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # price, timing, features, etc.
    severity = Column(Integer, default=50)  # 0-100 importance
    
    # Réponse
    response = Column(Text, nullable=True)
    response_generated_at = Column(DateTime, nullable=True)
    response_ai_model = Column(String(50), nullable=True)
    
    # Résultat
    resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    follow_up_needed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    prospect = relationship("Prospect", back_populates="objections")
    
    __table_args__ = (
        Index('idx_prospect_category', 'prospect_id', 'category'),
        Index('idx_resolved', 'resolved'),
    )

# ============================================================
# MODÈLE: AUDIT LOG (SÉCURITÉ)
# ============================================================

class AuditLog(Base):
    """Journal d'audit pour la sécurité"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Action
    action = Column(String(100), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    resource_type = Column(String(50), nullable=False, index=True)  # prospect, message, etc.
    resource_id = Column(Integer, nullable=True)
    
    # Détails
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    
    # Contexte
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_user_action', 'user_id', 'action'),
        Index('idx_resource', 'resource_type', 'resource_id'),
        Index('idx_created', 'created_at'),
    )

# ============================================================
# MODÈLE: SESSION
# ============================================================

class Session(Base):
    """Sessions utilisateur"""
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    is_revoked = Column(Boolean, default=False, index=True)
    
    __table_args__ = (
        Index('idx_user_token', 'user_id', 'token'),
    )

__all__ = [
    'Base',
    'Prospect',
    'Interaction',
    'Message',
    'Objection',
    'AuditLog',
    'Session',
    'ProspectStatus',
    'InteractionType',
    'MessageStatus',
    'SentimentScore',
]
"@

$content | Out-File -FilePath "src\database\models.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\database\models.py" -ForegroundColor Green