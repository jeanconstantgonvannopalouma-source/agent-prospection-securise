$content = @"
"""
Tests de la base de données
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_prospect_creation(test_session, test_prospect_data):
    """Test création prospect"""
    from database.repositories import ProspectRepository
    
    repo = ProspectRepository(test_session)
    prospect = repo.create(test_prospect_data)
    
    assert prospect is not None
    assert prospect.email == 'john.doe@test.com'
    assert prospect.first_name == 'John'

def test_prospect_retrieval(test_session, test_prospect_data):
    """Test récupération prospect"""
    from database.repositories import ProspectRepository
    
    repo = ProspectRepository(test_session)
    
    # Crée
    created = repo.create(test_prospect_data)
    
    # Récupère
    retrieved = repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.email == created.email

def test_prospect_update(test_session, test_prospect_data):
    """Test mise à jour prospect"""
    from database.repositories import ProspectRepository
    from database.models import ProspectStatus
    
    repo = ProspectRepository(test_session)
    
    # Crée
    prospect = repo.create(test_prospect_data)
    
    # Met à jour
    success = repo.update_status(prospect.id, ProspectStatus.CONTACTED)
    assert success == True
    
    # Vérifie
    updated = repo.get_by_id(prospect.id)
    assert updated.status == ProspectStatus.CONTACTED

def test_message_creation(test_session, test_prospect_data):
    """Test création message"""
    from database.repositories import ProspectRepository, MessageRepository
    
    repo_prospect = ProspectRepository(test_session)
    repo_message = MessageRepository(test_session)
    
    # Crée prospect
    prospect = repo_prospect.create(test_prospect_data)
    
    # Crée message
    message = repo_message.create(
        prospect_id=prospect.id,
        subject='Test Subject',
        body='Test body'
    )
    
    assert message is not None
    assert message.prospect_id == prospect.id

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
"@

$content | Out-File -FilePath "tests\test_database.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: tests\test_database.py" -ForegroundColor Green