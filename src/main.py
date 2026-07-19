import os
import re
import logging
import google.generativeai as genai
from datetime import datetime

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("agent")

app = Flask(__name__, static_folder="src/static", template_folder="src/templates")
CORS(app)

ENV                = os.getenv("ENV", "development").lower()
DATABASE_URL       = os.getenv("DATABASE_URL")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL       = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./agent_prospection.db"
    logger.warning("Mode local: SQLite utilisé.")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine       = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base         = declarative_base()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

class Prospect(Base):
    __tablename__ = "prospects"
    id                  = Column(Integer, primary_key=True)
    first_name          = Column(String(100), nullable=False, default="")
    last_name           = Column(String(100), nullable=False, default="")
    email               = Column(String(255), nullable=False, unique=True)
    company             = Column(String(255), nullable=True)
    job_title           = Column(String(150), nullable=True)
    industry            = Column(String(100), nullable=True)
    country             = Column(String(2),   nullable=True)
    status              = Column(String(50),  default="nouveau")
    qualification_score = Column(Integer,     default=50)
    notes               = Column(Text,        nullable=True)
    created_at          = Column(DateTime,    default=datetime.utcnow)
    updated_at          = Column(DateTime,    default=datetime.utcnow)

def ensure_schema():
    insp = inspect(engine)
    if not insp.has_table("prospects"):
        Base.metadata.create_all(engine)
        logger.info("Table prospects créée.")
        return
    cols = {c["name"] for c in insp.get_columns("prospects")}
    for col, typ in [
        ("company","VARCHAR(255)"),("job_title","VARCHAR(150)"),
        ("industry","VARCHAR(100)"),("country","VARCHAR(2)"),
        ("status","VARCHAR(50)"),("qualification_score","INTEGER"),
        ("notes","TEXT"),("created_at","TIMESTAMP"),("updated_at","TIMESTAMP")
    ]:
        if col not in cols:
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE prospects ADD COLUMN {col} {typ}"))
                conn.commit()
    Base.metadata.create_all(engine)

ensure_schema()

def ask_gemini(prompt: str) -> str:
    """Appel Gemini centralisé"""
    try:
        model    = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Erreur Gemini: {e}")
        return f"Erreur IA: {str(e)}"

@app.before_request
def require_token():
    public = ["/", "/ui", "/health", "/api/admin/chat", "/api/admin/stats", "/favicon.ico"]
    if request.path in public:
        return None
    if request.path.startswith("/ui") or request.path.startswith("/static/"):
        return None
    if request.method == "OPTIONS":
        return None
    if not INTERNAL_API_TOKEN:
        return None
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {INTERNAL_API_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401
    return None

@app.route("/", methods=["GET"])
def root():
    return jsonify({"service": "agent-prospection", "status": "online", "ui": "/ui"}), 200

@app.route("/ui", methods=["GET"])
def ui():
    return render_template("templates/ui.html")

@app.route("/health", methods=["GET"])
def health():
    try:
        db    = SessionLocal()
        count = db.query(Prospect).count()
        db.close()
        return jsonify({"status": "healthy", "database": "ok", "prospects_count": count}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route("/api/prospects", methods=["POST"])
def create_prospect():
    data  = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "email requis"}), 400
    db = SessionLocal()
    try:
        existing = db.query(Prospect).filter(Prospect.email == email).first()
        if existing:
            return jsonify({"status": "exists", "id": existing.id, "email": existing.email}), 200
        prospect = Prospect(
            first_name          = (data.get("first_name") or "").strip(),
            last_name           = (data.get("last_name")  or "").strip(),
            email               = email,
            company             = (data.get("company")    or "").strip() or None,
            job_title           = (data.get("job_title")  or "").strip() or None,
            industry            = (data.get("industry")   or "").strip() or None,
            country             = (data.get("country")    or "").strip().upper() or None,
            status              = "nouveau",
            qualification_score = int(data.get("qualification_score") or 50),
            notes               = (data.get("notes")      or "").strip() or None
        )
        db.add(prospect)
        db.commit()
        db.refresh(prospect)
        return jsonify({"status": "success", "id": prospect.id, "email": prospect.email}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route("/api/prospects", methods=["GET"])
def list_prospects():
    limit = min(int(request.args.get("limit", 20)), 200)
    db    = SessionLocal()
    try:
        rows = db.query(Prospect).order_by(Prospect.id.desc()).limit(limit).all()
        return jsonify({
            "count": len(rows),
            "prospects": [
                {"id": r.id, "first_name": r.first_name, "last_name": r.last_name,
                 "email": r.email, "company": r.company, "job_title": r.job_title,
                 "industry": r.industry, "status": r.status}
                for r in rows
            ]
        }), 200
    finally:
        db.close()

@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json() or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message vide"}), 400
    db = SessionLocal()
    try:
        count    = db.query(Prospect).count()
        derniers = db.query(Prospect).order_by(Prospect.id.desc()).limit(5).all()
        liste    = "\n".join([
            f"- {p.first_name} {p.last_name} | {p.email} | {p.company} | {p.status}"
            for p in derniers
        ])
        prompt = (
            f"Tu es un agent de prospection expert pour 'Finance OS', un template Notion vendu 19€.\n"
            f"La base contient {count} prospects. Derniers prospects:\n{liste}\n\n"
            f"Instruction: {message}\n\n"
            f"Réponds en français, de façon concise et professionnelle."
        )
        reply = ask_gemini(prompt)
        return jsonify({"reply": reply}), 200
    except Exception as e:
        return jsonify({"reply": f"Erreur: {str(e)}"}), 500
    finally:
        db.close()

@app.route("/api/admin/chat", methods=["POST"])
def admin_chat():
    data        = request.get_json() or {}
    instruction = (data.get("instruction") or "").strip()
    if not instruction:
        return jsonify({"error": "Instruction vide."}), 400
    db = SessionLocal()
    try:
        count    = db.query(Prospect).count()
        prospects = db.query(Prospect).order_by(Prospect.id.desc()).limit(20).all()
        liste    = "\n".join([
            f"- ID:{p.id} | {p.first_name} {p.last_name} | {p.email} | {p.company} | {p.job_title} | {p.industry} | {p.status}"
            for p in prospects
        ])
        prompt = (
            f"Tu es un agent de prospection expert pour 'Finance OS', un template Notion vendu 19€.\n"
            f"Tu peux: compter les prospects, rédiger des emails ultra-personnalisés, lister des prospects.\n"
            f"Base de données ({count} prospects):\n{liste}\n\n"
            f"Quand tu rédiges un email: utilise le prénom, l'entreprise et le secteur.\n"
            f"Garde les emails courts (max 120 mots), chaleureux, orientés vers une seule action.\n\n"
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
        return jsonify({"error": f"Erreur Gemini: {str(e)}"}), 500
    finally:
        db.close()

@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    db = SessionLocal()
    try:
        total     = db.query(Prospect).count()
        nouveaux  = db.query(Prospect).filter(Prospect.status == "nouveau").count()
        contactes = db.query(Prospect).filter(Prospect.status == "contacté").count()
        return jsonify({"prospects_count": total, "new_count": nouveaux, "contacted_count": contactes}), 200
    finally:
        db.close()


# ============================================================
# DELETE PROSPECT
# ============================================================

@app.route("/api/prospects/<int:prospect_id>", methods=["DELETE"])
def delete_prospect(prospect_id):
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
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    logger.info(f"Starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)



