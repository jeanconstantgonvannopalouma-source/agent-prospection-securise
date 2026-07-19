$content = @"
"""
Paquet API
API REST et endpoints
"""

__all__ = ['routes', 'schemas', 'middleware']
"@

$content | Out-File -FilePath "src\api\__init__.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\api\__init__.py" -ForegroundColor Green