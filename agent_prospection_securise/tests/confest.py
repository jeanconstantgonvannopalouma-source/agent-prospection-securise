$content = @"
"""
Configuration pytest
Fixtures et setup pour les tests
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

@pytest.fixture
def test_config():
    """Configuration de test"""
    from config import TestingConfig
    return TestingConfig

@pytest.fixture
def test_db():
    """BD de test en mémoire"""
    from database.connection import DatabaseConnection
    db = DatabaseConnection()
    yield db
    # Cleanup
    from database.models import Base
    Base.metadata.drop_all(db._engine)

@pytest.fixture
def test_session(test_db):
    """Session BD de test"""
    session = test_db.get_session()
    yield session
    test_db.close_session(session)

@pytest.fixture
def test_prospect_data():
    """Données de test pour prospect"""
    return {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@test.com',
        'company': 'TestCorp',
        'job_title': 'Director',
        'industry': 'Tech',
        'country': 'FR'
    }
"@

$content | Out-File -FilePath "tests\conftest.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: tests\conftest.py" -ForegroundColor Green