$content = @"
"""
Paquet tests
"""

__all__ = []
"@

$content | Out-File -FilePath "tests\__init__.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: tests\__init__.py" -ForegroundColor Green