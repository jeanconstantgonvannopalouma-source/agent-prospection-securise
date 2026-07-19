$content = @"
"""
Paquet core
Logique métier centrale
"""

__all__ = ['agent', 'workflow']
"@

$content | Out-File -FilePath "src\core\__init__.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\core\__init__.py" -ForegroundColor Green