"""Modèles de base de données"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ProspectStatus(enum.Enum):
    NEW = "nouveau"
    CONTACTED = "contacté"
    QUALIFIED = "qualifié"
    DEMOING = "en_présentation"
    NEGOTIATING = "en_négociation"
    WON = "remporté"
    LOST = "perdu"

class Prospect(Base):
    __tablename__ = 'prospects'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    company_name = Column(String(255), nullable=False, index=True)
    job_title = Column(String(150), nullable=False)
    industry = Column(String(100), nullable=True)
    country = Column(String(2), nullable=True)
    company_size = Column(String(50), nullable=True)
    
    status = Column(Enum(ProspectStatus), default=ProspectStatus.NEW, index=True)
    qualification_score = Column(Integer, default=0)
    conversion_probability = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    interactions = relationship("Interaction", back_populates="prospect", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="prospect", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Prospect {self.first_name} {self.last_name} ({self.email})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'company': self.company_name,
            'job_title': self.job_title,
            'status': self.status.value if self.status else None,
            'qualification_score': self.qualification_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class Interaction(Base):
    __tablename__ = 'interactions'
    
    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False, index=True)
    
    type = Column(String(50), nullable=False)
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    
    response_received = Column(Boolean, default=False)
    response_content = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    prospect = relationship("Prospect", back_populates="interactions")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False, index=True)
    
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    
    channel = Column(String(50), nullable=False)
    status = Column(String(50), default="draft")
    
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    
    prospect = relationship("Prospect", back_populates="messages")
