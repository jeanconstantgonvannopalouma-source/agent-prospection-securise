$content = @"
"""
Paquet de sécurité
Module central pour toute la sécurité de l'application
"""

__all__ = ['encryption', 'validation', 'rate_limiter', 'auth', 'sanitizer']
"@

$content | Out-File -FilePath "src\security\__init__.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\security\__init__.py" -ForegroundColor Green