import os
import re
import json
import logging
import google.generativeai as genai
from datetime import datetime

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

# ============================================================
# CONFIGURATION
# ============================================================

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("agent")

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Configuration des variables d'environnement
ENV = os.getenv("ENV", "development").lower()
DATABASE_URL = os.getenv("DATABASE_URL")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Correction de l'URL PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuration de la base de données
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./agent_prospection.db"
    logger.warning("Mode local: SQLite utilisé.")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Configuration de Gemini
genai.configure(api_key=GEMINI_API_KEY)

class Prospect(Base):
    __tablename__ = "prospects"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False, default="")
    last_name = Column(String(100), nullable=False, default="")
    email = Column(String(255), nullable=False, unique=True)
    company = Column(String(255), nullable=True)
    job_title = Column(String(150), nullable=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(2), nullable=True)
    status = Column(String(50), default="nouveau")
    qualification_score = Column(Integer, default=50)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

def ensure_schema():
    """Vérifie et crée le schéma de la base de données"""
    insp = inspect(engine)
    if not insp.has_table("prospects"):
        Base.metadata.create_all(engine)
        logger.info("Table prospects créée.")
        return

    cols = {c["name"] for c in insp.get_columns("prospects")}
    missing = []

    for col, typ in [
        ("company", "VARCHAR(255)"),
        ("job_title", "VARCHAR(150)"),
        ("industry", "VARCHAR(100)"),
        ("country", "VARCHAR(2)"),
        ("status", "VARCHAR(50)"),
        ("qualification_score", "INTEGER"),
        ("notes", "TEXT"),
        ("created_at", "TIMESTAMP"),
        ("updated_at", "TIMESTAMP")
    ]:
        if col not in cols:
            missing.append((col, typ))

    if missing:
        logger.warning(f"Colonnes manquantes détectées: {missing}")
        with engine.connect() as conn:
            for name, typ in missing:
                conn.execute(text(f"ALTER TABLE prospects ADD COLUMN {name} {typ}"))
            conn.commit()
        logger.info("Migration automatique effectuée.")

    Base.metadata.create_all(engine)

def ask_gemini(prompt: str) -> str:
    """Interroge Gemini avec un prompt"""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Erreur Gemini: {e}")
        return f"Erreur IA: {str(e)}"

# ============================================================
# MIDDLEWARE DE SÉCURITÉ
# ============================================================

@app.before_request
def require_token():
    """Vérifie le token d'authentification"""
    public_paths = [
        "/", "/ui", "/health", "/api/admin/chat",
        "/api/admin/stats", "/favicon.ico"
    ]

    if request.path in public_paths:
        return None

    if request.path.startswith("/static/") or request.path.startswith("/src/static/"):
        return None

    if request.method == "OPTIONS":
        return None

    if not INTERNAL_API_TOKEN:
        return None

    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {INTERNAL_API_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

# ============================================================
# ROUTES PUBLIQUES
# ============================================================

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "agent-prospection",
        "status": "online",
        "ui": "/ui",
        "health": "/health"
    }), 200

@app.route("/ui", methods=["GET"])
def ui():
    """Interface utilisateur avec animations Lottie"""
    try:
        return render_template("src/templates/ui.html")
    except Exception as e:
        logger.error(f"Erreur template: {e}")
        return jsonify({
            "error": "Template not found",
            "details": str(e),
            "help": "Vérifiez que src/templates/ui.html existe"
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """Vérification de santé du service"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        db = SessionLocal()
        try:
            count = db.query(Prospect).count()
        finally:
            db.close()

        return jsonify({
            "status": "healthy",
            "database": "ok",
            "prospects_count": count,
            "gemini": "configured" if GEMINI_API_KEY else "missing"
        }), 200

    except Exception as e:
        logger.exception("Erreur health")
        return jsonify({
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }), 500

# ============================================================
# API PROSPECTS
# ============================================================

@app.route("/api/prospects", methods=["POST"])
def create_prospect():
    """Crée un nouveau prospect"""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "email requis"}), 400

    db = SessionLocal()
    try:
        existing = db.query(Prospect).filter(Prospect.email == email).first()
        if existing:
            return jsonify({
                "status": "exists",
                "id": existing.id,
                "email": existing.email
            }), 200

        prospect = Prospect(
            first_name=(data.get("first_name") or "").strip(),
            last_name=(data.get("last_name") or "").strip(),
            email=email,
            company=(data.get("company") or "").strip() or None,
            job_title=(data.get("job_title") or "").strip() or None,
            industry=(data.get("industry") or "").strip() or None,
            country=(data.get("country") or "").strip().upper() or None,
            status="nouveau",
            qualification_score=int(data.get("qualification_score") or 50),
            notes=(data.get("notes") or "").strip() or None
        )

        db.add(prospect)
        db.commit()
        db.refresh(prospect)

        return jsonify({
            "status": "success",
            "id": prospect.id,
            "email": prospect.email
        }), 201

    except Exception as e:
        db.rollback()
        logger.exception("Erreur création prospect")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route("/api/prospects", methods=["GET"])
def list_prospects():
    """Liste les prospects"""
    limit = min(int(request.args.get("limit", 20)), 200)
    db = SessionLocal()
    try:
        rows = db.query(Prospect).order_by(Prospect.id.desc()).limit(limit).all()
        return jsonify({
            "count": len(rows),
            "prospects": [
                {
                    "id": r.id,
                    "first_name": r.first_name,
                    "last_name": r.last_name,
                    "email": r.email,
                    "company": r.company,
                    "job_title": r.job_title,
                    "industry": r.industry,
                    "country": r.country,
                    "status": r.status,
                    "score": r.qualification_score
                }
                for r in rows
            ]
        }), 200
    except Exception as e:
        logger.exception("Erreur listage prospects")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route("/api/prospects/<int:prospect_id>", methods=["DELETE"])
def delete_prospect(prospect_id):
    """Supprime un prospect"""
    db = SessionLocal()
    try:
        prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
        if not prospect:
            return jsonify({"error": "Prospect non trouvé"}), 404

        db.delete(prospect)
        db.commit()
        return jsonify({"status": "success", "message": f"Prospect {prospect_id} supprimé"}), 200
    except Exception as e:
        db.rollback()
        logger.exception("Erreur suppression prospect")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

# ============================================================
# CHAT AVEC GEMINI (conserve tes animations Lottie)
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():
    """Interface de chat avec l'agent (conserve tes animations)"""
    data = request.get_json() or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "message vide"}), 400

    db = SessionLocal()
    try:
        count = db.query(Prospect).count()
        derniers = db.query(Prospect).order_by(Prospect.id.desc()).limit(5).all()
        liste = "\n".join([
            f"- {p.first_name} {p.last_name} | {p.email} | {p.company} | {p.status}"
            for p in derniers
        ])

        prompt = (
            f"Tu es un agent de prospection expert pour 'Finance OS', un template Notion vendu 19€.\n"
            f"La base contient {count} prospects. Voici les derniers:\n{liste}\n\n"
            f"Instruction: {message}\n\n"
            f"Réponds en français, de façon concise et professionnelle.\n"
            f"Conserve le style des animations Lottie et de l'interface existante."
        )

        reply = ask_gemini(prompt)
        return jsonify({"reply": reply}), 200

    except Exception as e:
        logger.exception("Erreur chat")
        return jsonify({"reply": f"Erreur: {str(e)}"}), 500
    finally:
        db.close()

@app.route("/api/admin/chat", methods=["POST"])
def admin_chat():
    """Interface admin avec accès à la base de données"""
    data = request.get_json() or {}
    instruction = (data.get("instruction") or "").strip()

    if not instruction:
        return jsonify({"error": "Instruction vide."}), 400

    db = SessionLocal()
    try:
        count = db.query(Prospect).count()
        prospects = db.query(Prospect).order_by(Prospect.id.desc()).limit(20).all()
        liste = "\n".join([
            f"- ID:{p.id} | {p.first_name} {p.last_name} | {p.email} | {p.company} | {p.job_title} | {p.industry} | {p.status}"
            for p in prospects
        ])

        prompt = (
            f"Tu es un agent de prospection expert pour 'Finance OS', un template Notion vendu 19€.\n"
            f"Tu peux: compter les prospects, rédiger des emails ultra-personnalisés, lister des prospects.\n"
            f"Base de données ({count} prospects):\n{liste}\n\n"
            f"Quand tu rédiges un email: utilise le prénom, l'entreprise et le secteur.\n"
            f"Garde les emails courts (max 120 mots), chaleureux et orientés vers une seule action.\n"
            f"Conserve le style des animations Lottie dans tes réponses.\n\n"
            f"Instruction: {instruction}\n\n"
            f"Réponds en français."
        )

        answer = ask_gemini(prompt)
        return jsonify({
            "status": "success",
            "answer": answer,
            "prospects_count": count
        }), 200

    except Exception as e:
        logger.exception("Erreur admin chat")
        return jsonify({"error": f"Erreur IA: {str(e)}"}), 500
    finally:
        db.close()

@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    """Statistiques de la base de données"""
    db = SessionLocal()
    try:
        total = db.query(Prospect).count()
        nouveaux = db.query(Prospect).filter(Prospect.status == "nouveau").count()
        contactes = db.query(Prospect).filter(Prospect.status == "contacté").count()
        return jsonify({
            "prospects_count": total,
            "new_count": nouveaux,
            "contacted_count": contactes
        }), 200
    except Exception as e:
        logger.exception("Erreur stats")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

# ============================================================
# DÉMARRAGE
# ============================================================

if __name__ == "__main__":
    ensure_schema()
    port = int(os.environ.get("PORT", "5000"))
    logger.info(f"Starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)


