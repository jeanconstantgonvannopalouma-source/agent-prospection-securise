$content = @"
# ============================================================
# SCRIPT SETUP - AGENT PROSPECTION
# Exécute EN TANT QU'ADMINISTRATEUR
# ============================================================

Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  SETUP - AGENT DE PROSPECTION SECURISE               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# 1. Vérifie Python
Write-Host "`n1️⃣ Vérification Python..." -ForegroundColor Yellow
python --version
if (`$LASTEXITCODE -ne 0) {
    Write-Host "❌ Python non trouvé. Installe depuis https://www.python.org/" -ForegroundColor Red
    exit 1
}

# 2. Crée venv
Write-Host "`n2️⃣ Création environnement virtuel..." -ForegroundColor Yellow
python -m venv venv
.\venv\Scripts\Activate.ps1
Write-Host "✓ Environnement créé" -ForegroundColor Green

# 3. Installe pip
Write-Host "`n3️⃣ Mise à jour pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel
Write-Host "✓ pip à jour" -ForegroundColor Green

# 4. Installe dépendances
Write-Host "`n4️⃣ Installation dépendances..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ Dépendances installées" -ForegroundColor Green

# 5. Génère clés
Write-Host "`n5️⃣ Génération des clés secrètes..." -ForegroundColor Yellow
python generate_secrets.py

# 6. Copie .env
if (-not (Test-Path ".env")) {
    Write-Host "`n6️⃣ Création .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Édite .env avec tes clés API!" -ForegroundColor Yellow
}

Write-Host "`n✓✓✓ SETUP COMPLÈTE! ✓✓✓" -ForegroundColor Green
Write-Host "`nProchaines étapes:" -ForegroundColor Cyan
Write-Host "1. Édite le fichier .env" -ForegroundColor Yellow
Write-Host "2. Lance: python src/main.py" -ForegroundColor Yellow
"@

$content | Out-File -FilePath "setup.ps1" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: setup.ps1" -ForegroundColor Green