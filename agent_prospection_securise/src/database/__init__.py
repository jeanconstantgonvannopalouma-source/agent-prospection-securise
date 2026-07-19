$content = @"
"""
Paquet base de données
Gère toute la persistance des données
"""

__all__ = ['models', 'connection', 'repositories', 'migrations']
"@

$content | Out-File -FilePath "src\database\__init__.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\database\__init__.py" -ForegroundColor Green