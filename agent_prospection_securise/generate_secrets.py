$content = @"
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Générateur de clés secrètes
À exécuter UNE SEULE FOIS pour générer les clés
"""

import secrets
from cryptography.fernet import Fernet
import os

print("\n" + "="*70)
print(" GÉNÉRATEUR DE CLÉS SECRÈTES - AGENT PROSPECTION")
print("="*70 + "\n")

# Génère SECRET_KEY
secret_key = secrets.token_urlsafe(32)
print(f"SECRET_KEY={secret_key}\n")

# Génère ENCRYPTION_KEY
encryption_key = Fernet.generate_key().decode()
print(f"ENCRYPTION_KEY={encryption_key}\n")

# Génère INTERNAL_API_TOKEN
api_token = secrets.token_urlsafe(64)
print(f"INTERNAL_API_TOKEN={api_token}\n")

print("="*70)
print("\n⚠️  INSTRUCTIONS:")
print("1. Ouvre le fichier .env")
print("2. Remplace les valeurs par celles ci-dessus")
print("3. Sauvegarde le fichier")
print("4. NE PARTAGE PAS CES CLÉS!")
print("\n" + "="*70 + "\n")

# Optionnel: sauvegarde dans un fichier temporaire
save_to_file = input("Sauvegarder dans secrets_temp.txt? (o/n): ").lower()
if save_to_file == 'o':
    with open('secrets_temp.txt', 'w') as f:
        f.write(f"SECRET_KEY={secret_key}\n")
        f.write(f"ENCRYPTION_KEY={encryption_key}\n")
        f.write(f"INTERNAL_API_TOKEN={api_token}\n")
    print("✓ Sauvegardé dans secrets_temp.txt")
    print("⚠️  Supprime ce fichier après l'avoir utilisé!\n")
"@

$content | Out-File -FilePath "generate_secrets.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: generate_secrets.py" -ForegroundColor Green