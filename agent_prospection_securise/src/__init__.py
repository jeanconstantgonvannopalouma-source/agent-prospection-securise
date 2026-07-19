$content = @"
"""
Agent de Prospection Sécurisé
Package principal
"""

__version__ = '1.0.0'
__author__ = 'Prospection AI Team'
__all__ = ['config', 'security', 'database', 'modules', 'core', 'api']
"@

$content | Out-File -FilePath "src\__init__.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\__init__.py" -ForegroundColor Green