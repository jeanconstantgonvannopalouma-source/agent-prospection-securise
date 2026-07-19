$content = @"
# Script de démarrage rapide

param(
    [switch]\$Install = \$false,
    [switch]\$Test = \$false,
    [switch]\$Run = \$false
)

# Active l'environnement
Write-Host "🔧 Activation environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

if (\$Install) {
    Write-Host "📦 Installation dépendances..." -ForegroundColor Yellow
    pip install -r requirements.txt --upgrade
}

if (\$Test) {
    Write-Host "🧪 Lancement tests..." -ForegroundColor Yellow
    python src/main.py
}

if (\$Run) {
    Write-Host "🚀 Démarrage application..." -ForegroundColor Green
    python src/main.py
}

if (-not \$Install -and -not \$Test -and -not \$Run) {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\start_project.ps1 -Run         # Démarre l'app"
    Write-Host "  .\start_project.ps1 -Install     # Installe dépendances"
    Write-Host "  .\start_project.ps1 -Test -Run   # Tests puis app"
}
"@

$content | Out-File -FilePath "start_project.ps1" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: start_project.ps1" -ForegroundColor Green