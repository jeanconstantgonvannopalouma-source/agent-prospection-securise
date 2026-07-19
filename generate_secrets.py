import secrets
from cryptography.fernet import Fernet

print("GÉNÉRATEUR DE CLÉS")
print("=" * 50)

secret_key = secrets.token_urlsafe(32)
print(f"SECRET_KEY={secret_key}")

encryption_key = Fernet.generate_key().decode()
print(f"ENCRYPTION_KEY={encryption_key}")

api_token = secrets.token_urlsafe(64)
print(f"INTERNAL_API_TOKEN={api_token}")

print("=" * 50)
print("Copie ces valeurs dans .env")
