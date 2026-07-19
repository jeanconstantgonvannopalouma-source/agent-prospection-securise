$content = @"
"""
Tests des modules de sécurité
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_encryption():
    """Test chiffrement"""
    from security.encryption import encryption
    
    data = "secret_data"
    encrypted = encryption.encrypt_data(data)
    decrypted = encryption.decrypt_data(encrypted)
    
    assert decrypted == data
    assert encrypted != data

def test_validation_email():
    """Test validation email"""
    from security.validation import validator
    
    assert validator.validate_email('john@example.com') == True
    assert validator.validate_email('invalid.email') == False
    assert validator.validate_email('') == False

def test_validation_phone():
    """Test validation téléphone"""
    from security.validation import validator
    
    assert validator.validate_phone('+33612345678') == True
    assert validator.validate_phone('invalid') == False

def test_rate_limiter():
    """Test rate limiting"""
    from security.rate_limiter import rate_limiter
    
    # Doit être autorisé
    is_allowed, msg = rate_limiter.is_allowed('test_user')
    assert is_allowed == True
    
    # Stats
    stats = rate_limiter.get_stats('test_user')
    assert 'requests_per_minute' in stats

def test_sanitizer():
    """Test nettoyage données"""
    from security.sanitizer import sanitizer
    
    # Test XSS
    dangerous = "<script>alert('xss')</script>"
    clean = sanitizer.sanitize_string(dangerous)
    assert '<script>' not in clean
    assert 'alert' not in clean
    
    # Test SQL
    sql_injection = "'; DROP TABLE users;--"
    has_injection = sanitizer.remove_sql_keywords(sql_injection)
    assert has_injection == True

@pytest.mark.asyncio
async def test_jwt_auth():
    """Test authentification JWT"""
    from security.auth import jwt_auth
    
    # Génère token
    token = jwt_auth.generate_token('user123', 'user@example.com')
    assert token
    
    # Vérifie token
    is_valid, payload, msg = jwt_auth.verify_token(token)
    assert is_valid == True
    assert payload['user_id'] == 'user123'
    assert payload['email'] == 'user@example.com'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
"@

$content | Out-File -FilePath "tests\test_security.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: tests\test_security.py" -ForegroundColor Green