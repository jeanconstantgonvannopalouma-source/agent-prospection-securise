$content = @"
# 🚀 Agent de Prospection Sécurisé v1.0

Plateforme complète de prospection B2B alimentée par l'IA avec sécurité ultra-robuste.

## ✨ Caractéristiques

- **🤖 IA Avancée**: GPT-4 pour messages personnalisés
- **🔐 Sécurité Ultra**: AES-256, JWT, Rate Limiting, Validation entrées
- **📊 Analytics**: Dashboard temps réel, KPIs, Conversion Tracking
- **⚡ Automation**: Workflows automatisés, Scheduling
- **🗄️ BD Robuste**: SQLite/PostgreSQL, Migrations, Audit Logs
- **🌐 API REST**: Endpoints sécurisés et validés

## 🚀 Quickstart

\`\`\`bash
# 1. Clone et setup
cd agent_prospection_securise

# 2. Crée l'environnement
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Installe les dépendances
pip install -r requirements.txt

# 4. Configure .env
cp .env.example .env
# Édite .env avec tes clés API

# 5. Lance l'app
python src/main.py
\`\`\`

## 📁 Structure

\`\`\`
src/
├── config.py              # Configuration centrale
├── main.py                # Point d'entrée
├── security/              # Modules sécurité
├── database/              # Modèles & repositories
├── modules/               # Logique métier
├── core/                  # Agent principal
└── api/                   # Routes API

tests/                      # Tests unitaires
requirements.txt           # Dépendances
.env.example              # Template variables
\`\`\`

## 🔐 Sécurité

- ✅ Chiffrement AES-256 pour données sensibles
- ✅ Authentification JWT
- ✅ Rate Limiting (requêtes/minute/heure)
- ✅ Validation complète des entrées
- ✅ Protection XSS, SQL Injection
- ✅ Audit Logs de toutes les actions
- ✅ Sessions sécurisées
- ✅ Headers de sécurité HTTP

## 📚 Documentation

- `SECURITY.md` - Guide sécurité détaillé
- `API.md` - Documentation API
- Docstrings dans le code Python

## 🧪 Tests

\`\`\`bash
pytest tests/ -v --cov=src
\`\`\`

## 📄 Licence

MIT

## 👨‍💻 Auteur

Prospection AI Team
"@

$content | Out-File -FilePath "README.md" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: README.md" -ForegroundColor Green