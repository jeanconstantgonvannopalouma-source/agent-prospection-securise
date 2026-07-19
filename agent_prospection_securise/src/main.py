"""
API Production - Agent Prospection
Framework : Flask
Base de données : PostgreSQL
Déploiement : Render

Routes principales :
GET  /health
GET  /api/prospects
POST /api/prospects

Interface privée :
GET  /login
GET  /logout
GET  /admin
GET  /api/admin/stats
POST /api/admin/chat
"""

import os
import hmac
import logging
from datetime import datetime
from typing import Optional

from flask import Flask, jsonify, request, session
from werkzeug.middleware.proxy_fix import ProxyFix

from sqlalchemy import (
    create_engine,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    inspect,
    text,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# LOGS
# ============================================================

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent-prospection")


# ============================================================
# APPLICATION FLASK
# ============================================================

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static",
)

# Render utilise un proxy HTTPS devant Flask/Gunicorn.
# Cela permet à Flask de reconnaître correctement HTTPS.
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1,
)


# ============================================================
# CONFIGURATION ENVIRONNEMENT
# ============================================================

ENV = os.getenv("ENV", "development").lower()

INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")

DATABASE_URL = os.getenv("DATABASE_URL")


def normalize_database_url(url: Optional[str]) -> Optional[str]:
    """
    Render fournit parfois postgres://.
    SQLAlchemy moderne attend postgresql://.
    """
    if not url:
        return None

    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)

    return url


DATABASE_URL = normalize_database_url(DATABASE_URL)

# En production, PostgreSQL est obligatoire.
if ENV == "production" and not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL manquant en production. "
        "Ajoute DATABASE_URL dans Render > Environment."
    )

# Base SQLite uniquement pour les tests locaux.
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./agent_prospection.db"
    logger.warning(
        "Mode développement : SQLite est utilisé. "
        "Ne jamais utiliser SQLite en production."
    )

# Sécurité : le token API doit exister en production.
if ENV == "production" and not INTERNAL_API_TOKEN:
    raise RuntimeError(
        "INTERNAL_API_TOKEN manquant en production. "
        "Ajoute INTERNAL_API_TOKEN dans Render > Environment."
    )


# ============================================================
# BASE DE DONNEES SQLALCHEMY
# ============================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


# ============================================================
# MODELE PROSPECT
# ============================================================

class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True)

    first_name = Column(
        String(100),
        nullable=False,
        default=""
    )

    last_name = Column(
        String(100),
        nullable=False,
        default=""
    )

    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    company = Column(
        String(255),
        nullable=True,
    )

    job_title = Column(
        String(150),
        nullable=True,
    )

    industry = Column(
        String(100),
        nullable=True,
    )

    country = Column(
        String(2),
        nullable=True,
    )

    # nouveau / brouillon / approuvé / contacté / erreur / désinscrit
    status = Column(
        String(50),
        nullable=False,
        default="nouveau",
        index=True,
    )

    qualification_score = Column(
        Integer,
        nullable=False,
        default=0,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


# ============================================================
# INITIALISATION / MIGRATION SIMPLE
# ============================================================

def ensure_schema():
    """
    Crée la table prospects si elle n'existe pas.

    Cette fonction ajoute aussi quelques colonnes simples
    si une ancienne version de la base n'en possède pas.

    Pour un projet plus avancé, on utilisera Alembic.
    """

    inspector = inspect(engine)

    if not inspector.has_table("prospects"):
        logger.info("Création de la table prospects...")
        Base.metadata.create_all(engine)
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("prospects")
    }

    migrations = []

    if "company" not in existing_columns:
        migrations.append(
            ("company", "VARCHAR(255)")
        )

    if "job_title" not in existing_columns:
        migrations.append(
            ("job_title", "VARCHAR(150)")
        )

    if "industry" not in existing_columns:
        migrations.append(
            ("industry", "VARCHAR(100)")
        )

    if "country" not in existing_columns:
        migrations.append(
            ("country", "VARCHAR(2)")
        )

    if "notes" not in existing_columns:
        migrations.append(
            ("notes", "TEXT")
        )

    if "qualification_score" not in existing_columns:
        migrations.append(
            ("qualification_score", "INTEGER DEFAULT 0")
        )

    if "status" not in existing_columns:
        migrations.append(
            ("status", "VARCHAR(50) DEFAULT 'nouveau'")
        )

    if migrations:
        logger.warning(
            "Migration automatique des colonnes : %s",
            migrations,
        )

        with engine.connect() as connection:
            for column_name, column_type in migrations:
                query = (
                    f"ALTER TABLE prospects "
                    f"ADD COLUMN {column_name} {column_type}"
                )

                connection.execute(text(query))

            connection.commit()

    Base.metadata.create_all(engine)


ensure_schema()


# ============================================================
# OUTILS BASE DE DONNEES
# ============================================================

def db_session():
    """Retourne une session SQLAlchemy."""
    return SessionLocal()


def prospect_to_dict(prospect: Prospect) -> dict:
    """Transforme un prospect SQLAlchemy en JSON."""

    return {
        "id": prospect.id,
        "first_name": prospect.first_name,
        "last_name": prospect.last_name,
        "email": prospect.email,
        "company": prospect.company,
        "job_title": prospect.job_title,
        "industry": prospect.industry,
        "country": prospect.country,
        "status": prospect.status,
        "qualification_score": prospect.qualification_score,
        "notes": prospect.notes,
        "created_at": (
            prospect.created_at.isoformat()
            if prospect.created_at
            else None
        ),
        "updated_at": (
            prospect.updated_at.isoformat()
            if prospect.updated_at
            else None
        ),
    }


# ============================================================
# SECURITE DES ROUTES
# ============================================================

@app.before_request
def require_token():
    """
    Protège les routes API avec INTERNAL_API_TOKEN.

    Les pages admin utilisent une session privée après connexion.
    Les fichiers statiques restent accessibles afin de charger
    background.jpg et les futurs fichiers CSS/JS.
    """

    # Routes publiques nécessaires
    public_routes = [
        "/",
        "/health",
        "/login",
        "/logout",
        "/admin",
    ]

    if request.path in public_routes:
        return None

    # Important : permet de charger background.jpg.
    if request.path.startswith("/static/"):
        return None

    # Requête automatique envoyée par le navigateur avant certaines API.
    if request.method == "OPTIONS":
        return None

    # L'utilisateur connecté à l'interface admin peut utiliser
    # les routes admin sans mettre INTERNAL_API_TOKEN dans le navigateur.
    if (
        request.path.startswith("/api/admin/")
        and session.get("admin_logged_in")
    ):
        return None

    # En développement seulement, si aucun token est configuré,
    # l'API reste disponible afin de faciliter les tests locaux.
    if ENV != "production" and not INTERNAL_API_TOKEN:
        return None

    # Vérification du token Bearer.
    authorization = request.headers.get("Authorization", "")
    expected_token = f"Bearer {INTERNAL_API_TOKEN}"

    if not hmac.compare_digest(authorization, expected_token):
        return jsonify({
            "error": "Unauthorized"
        }), 401

    return None


# ============================================================
# ROUTES PUBLIQUES
# ============================================================

@app.route("/", methods=["GET"])
def home():
    """
    Retourne les informations minimales sur le service.
    """

    database_type = (
        "postgres"
        if "postgres" in DATABASE_URL
        else "sqlite"
    )

    return jsonify({
        "service": "agent-prospection",
        "environment": ENV,
        "database": database_type,
        "status": "running",
        "endpoints": [
            "/health",
            "/api/prospects (GET/POST)",
            "/admin",
        ],
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """
    Vérifie que l'API et la base PostgreSQL sont fonctionnelles.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        db = db_session()

        try:
            prospects_count = db.query(Prospect).count()
        finally:
            db.close()

        return jsonify({
            "status": "healthy",
            "database": "ok",
            "prospects_count": prospects_count,
            "environment": ENV,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200

    except Exception as error:
        logger.exception("Health check failed")

        return jsonify({
            "status": "unhealthy",
            "database": "error",
            "timestamp": datetime.utcnow().isoformat(),
        }), 500


# ============================================================
# API PROSPECTS
# ============================================================

@app.route("/api/prospects", methods=["POST"])
def create_prospect():
    """
    Ajoute un prospect.

    Exemple de JSON :

    {
      "first_name": "Jean",
      "last_name": "Dupont",
      "email": "jean.dupont@example.com",
      "company": "Exemple SAS",
      "job_title": "Directeur commercial",
      "industry": "Technologie",
      "country": "FR",
      "notes": "Prospect ajouté depuis l'interface"
    }
    """

    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({
            "error": "email requis"
        }), 400

    # Validation simple supplémentaire.
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({
            "error": "format email invalide"
        }), 400

    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    company = (data.get("company") or "").strip() or None
    job_title = (data.get("job_title") or "").strip() or None
    industry = (data.get("industry") or "").strip() or None
    country = (data.get("country") or "").strip().upper() or None
    notes = (data.get("notes") or "").strip() or None

    if country and len(country) != 2:
        return jsonify({
            "error": "country doit contenir un code pays de 2 lettres, par exemple FR"
        }), 400

    db = db_session()

    try:
        existing_prospect = (
            db.query(Prospect)
            .filter(Prospect.email == email)
            .first()
        )

        if existing_prospect:
            return jsonify({
                "status": "exists",
                "message": "Ce prospect existe déjà.",
                "prospect": prospect_to_dict(existing_prospect),
            }), 200

        prospect = Prospect(
            first_name=first_name,
            last_name=last_name,
            email=email,
            company=company,
            job_title=job_title,
            industry=industry,
            country=country,
            notes=notes,
            status="nouveau",
            qualification_score=50,
        )

        db.add(prospect)
        db.commit()
        db.refresh(prospect)

        logger.info(
            "Prospect créé : id=%s email=%s",
            prospect.id,
            prospect.email,
        )

        return jsonify({
            "status": "success",
            "message": "Prospect ajouté avec succès.",
            "prospect": prospect_to_dict(prospect),
        }), 201

    except IntegrityError:
        db.rollback()

        return jsonify({
            "error": "Ce prospect existe déjà."
        }), 409

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while creating prospect")

        return jsonify({
            "error": "Erreur base de données."
        }), 500

    except Exception:
        db.rollback()
        logger.exception("Unexpected error while creating prospect")

        return jsonify({
            "error": "Erreur interne du serveur."
        }), 500

    finally:
        db.close()


@app.route("/api/prospects", methods=["GET"])
def list_prospects():
    """
    Liste les prospects.

    Paramètres possibles :
    /api/prospects?limit=50
    /api/prospects?status=nouveau
    /api/prospects?country=FR
    /api/prospects?search=entreprise
    """

    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        limit = 50

    limit = min(max(limit, 1), 200)

    status = (request.args.get("status") or "").strip().lower()
    country = (request.args.get("country") or "").strip().upper()
    search = (request.args.get("search") or "").strip()

    db = db_session()

    try:
        query = db.query(Prospect)

        if status:
            query = query.filter(Prospect.status == status)

        if country:
            query = query.filter(Prospect.country == country)

        if search:
            like_value = f"%{search}%"

            query = query.filter(
                (Prospect.first_name.ilike(like_value))
                | (Prospect.last_name.ilike(like_value))
                | (Prospect.email.ilike(like_value))
                | (Prospect.company.ilike(like_value))
            )

        prospects = (
            query
            .order_by(Prospect.id.desc())
            .limit(limit)
            .all()
        )

        return jsonify({
            "count": len(prospects),
            "limit": limit,
            "prospects": [
                prospect_to_dict(prospect)
                for prospect in prospects
            ],
        }), 200

    except SQLAlchemyError:
        logger.exception("Database error while listing prospects")

        return jsonify({
            "error": "Erreur base de données."
        }), 500

    finally:
        db.close()


# ============================================================
# GESTION ERREURS GLOBALES
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Route introuvable."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Méthode HTTP non autorisée."
    }), 405


@app.errorhandler(500)
def internal_error(error):
    logger.exception("Internal server error")

    return jsonify({
        "error": "Erreur interne du serveur."
    }), 500


# ============================================================
# INITIALISATION INTERFACE ADMIN
# ============================================================

# Cette importation doit être placée APRES la création de :
# - app
# - db_session
# - Prospect
#
# admin_interface.py reçoit ces éléments via init_admin_interface().

from admin_interface import init_admin_interface

init_admin_interface(
    app=app,
    db_session=db_session,
    Prospect=Prospect,
)


# ============================================================
# LANCEMENT LOCAL UNIQUEMENT
# ============================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))

    logger.info(
        "Démarrage Agent Prospection sur port %s (ENV=%s)",
        port,
        ENV,
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )