import os
import re
import json
import logging
import google.generativeai as genai
from datetime import datetime

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

# ============================================================
# CONFIGURATION INITIALE (inchangée)
# ============================================================

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("agent")

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Configuration des variables d'environnement
ENV = os.getenv("ENV", "development").lower()
DATABASE_URL = os.getenv("DATABASE_URL")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Clé Gemini obligatoire

# Correction de l'URL PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./agent_prospection.db"
    logger.warning("Mode local: SQLite utilisé.")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# ============================================================
# CONFIGURATION GEMINI (CORRIGÉE)
# ============================================================

try:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("✅ Gemini configuré avec succès")
except Exception as e:
    logger.error(f"❌ Erreur Gemini: {e}")
    # On continue même si Gemini échoue pour ne pas bloquer l'application

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
    """Vérifie et crée le schéma de la base de données (inchangé)"""
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
    """Interroge Gemini avec gestion d'erreur robuste"""
    try:
        model = genai.GenerativeModel("gemini-pro")  # MODÈLE CORRIGÉ
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Erreur Gemini: {e}")
        return f"[Erreur IA: {str(e)}]"

# ============================================================
# MIDDLEWARE DE SÉCURITÉ (inchangé)
# ============================================================

@app.before_request
def require_token():
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
# ROUTES PUBLIQUES (CORRIGÉES)
# ============================================================

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "agent-prospection",
        "status": "online",
        "ui": "/ui",
        "health": "/health"
    }), 200

@app.route("/health", methods=["GET"])
def health():
    """Vérification de santé améliorée"""
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

@app.route("/ui", methods=["GET"])
def ui():
    """Interface utilisateur avec animations Lottie (CORRIGÉE)"""
    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent de Prospection</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, Helvetica, sans-serif;
            background: linear-gradient(135deg, #0f172a, #1e3a5f);
            color: white;
        }
        .container {
            width: min(1100px, calc(100% - 32px));
            margin: 0 auto;
            padding: 32px 0;
        }
        #lottie-header {
            width: 90px;
            height: 90px;
        }
        .message {
            max-width: 82%;
            margin: 10px 0;
            padding: 13px 15px;
            border-radius: 12px;
            background: white;
            color: #1e293b;
        }
        .user-message {
            margin-left: auto;
            background: #2563eb;
            color: white;
        }
        #prompt {
            flex: 1;
            min-width: 0;
            padding: 13px;
            border: 1px solid #cbd5e1;
            border-radius: 9px;
            font-size: 15px;
            outline: none;
        }
        #send-button {
            padding: 13px 18px;
            border: 0;
            border-radius: 9px;
            color: white;
            background: #2563eb;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <div id="lottie-header"></div>
        <h1>Agent de Prospection</h1>
        <div id="messages"></div>
        <div style="display: flex; gap: 10px; padding: 18px;">
            <input id="prompt" type="text" placeholder="Posez votre question..." autocomplete="off" required>
            <button id="send-button">Envoyer</button>
        </div>
    </div>

    <script>
        // Animations Lottie (inchangées)
        lottie.loadAnimation({
            container: document.getElementById("lottie-header"),
            renderer: "svg",
            loop: true,
            autoplay: true,
            path: "https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json"
        });

        // Chat amélioré avec gestion d'erreur
        document.getElementById("send-button").addEventListener("click", async () => {
            const prompt = document.getElementById("prompt").value;
            const messagesDiv = document.getElementById("messages");

            if (!prompt.trim()) return;

            // Affiche le message utilisateur
            const userMsg = document.createElement("div");
            userMsg.className = "message user-message";
            userMsg.textContent = prompt;
            messagesDiv.appendChild(userMsg);

            document.getElementById("prompt").value = "";
            document.getElementById("send-button").disabled = true;

            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer """ + INTERNAL_API_TOKEN + """"
                    },
                    body: JSON.stringify({ message: prompt })
                });

                if (!response.ok) {
                    throw new Error(`Erreur API: ${response.status}`);
                }

                const data = await response.json();
                const agentMsg = document.createElement("div");
                agentMsg.className = "message";
                agentMsg.textContent = data.reply;
                messagesDiv.appendChild(agentMsg);

            } catch (error) {
                const errorMsg = document.createElement("div");
                errorMsg.className = "message system-message";
                errorMsg.textContent = `Erreur: ${error.message}`;
                errorMsg.style.background = "#ffedd5";
                errorMsg.style.color = "#7c2d12";
                messagesDiv.appendChild(errorMsg);
            } finally {
                document.getElementById("send-button").disabled = false;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        });
    </script>
</body>
</html>"""
    return Response(html_content, mimetype="text/html")

# ============================================================
# API PROSPECTS (inchangée)
# ============================================================

@app.route("/api/prospects", methods=["POST"])
def create_prospect():
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

# [Le reste de tes routes API prospects...]

# ============================================================
# CHAT AVEC GEMINI (CORRIGÉ)
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():
    """Route de chat avec Gemini (CORRIGÉE)"""
    data = request.get_json() or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Message vide"}), 400

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
            f"Réponds en français, de façon concise et professionnelle."
        )

        reply = ask_gemini(prompt)
        return jsonify({"reply": reply}), 200

    except Exception as e:
        logger.exception("Erreur chat")
        return jsonify({
            "error": "Erreur interne",
            "details": str(e),
            "help": "Vérifiez votre clé API Gemini et le modèle gemini-pro"
        }), 500
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
