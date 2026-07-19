$content = @"
"""
Schemas Pydantic pour validation API
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from security.validation import InputValidator

validator_instance = InputValidator()

class ProspectCreate(BaseModel):
    """Schema création prospect"""
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(default="", max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    company: str = Field(..., min_length=2, max_length=255)
    job_title: Optional[str] = Field(None, max_length=150)
    industry: Optional[str] = None
    country: Optional[str] = None
    
    @validator('email')
    def validate_email_field(cls, v):
        if not validator_instance.validate_email(v):
            raise ValueError('Email invalide')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "company": "TechCorp",
                "job_title": "Director",
            }
        }

class ProspectUpdate(BaseModel):
    """Schema mise à jour prospect"""
    phone: Optional[str] = None
    job_title: Optional[str] = None
    qualification_score: Optional[int] = Field(None, ge=0, le=100)
    conversion_probability: Optional[float] = Field(None, ge=0.0, le=1.0)

class ProspectResponse(BaseModel):
    """Schema réponse prospect"""
    id: int
    first_name: str
    last_name: str
    email: str
    company: str
    job_title: str
    status: str
    qualification_score: int
    conversion_probability: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    """Schema création message"""
    prospect_id: int
    subject: str = Field(..., min_length=5, max_length=255)
    body: str = Field(..., min_length=10, max_length=5000)
    channel: str = Field(default="email")

class SearchRequest(BaseModel):
    """Schema recherche prospects"""
    industries: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    company_sizes: Optional[List[str]] = None
    limit: int = Field(default=50, le=500)

__all__ = ['ProspectCreate', 'ProspectUpdate', 'ProspectResponse', 'MessageCreate', 'SearchRequest']
"@

$content | Out-File -FilePath "src\api\schemas.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\api\schemas.py" -ForegroundColor Green