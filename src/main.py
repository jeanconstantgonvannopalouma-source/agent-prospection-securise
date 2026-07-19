import os
import re
import json
import logging
import google.generativeai as genai
from datetime import datetime

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# ============================================================
# CONFIGURATION
# ============================================================

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("agent")

app = Flask(__name__)
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

# [Le reste de tes modèles et fonctions existantes...]

# ============================================================
# INTERFACE UI DIRECTEMENT DANS FLASK (SOLUTION ULTIME)
# ============================================================

@app.route("/ui")
def ui():
    """Interface utilisateur SANS TEMPLATE"""
    html_content = """
<!DOCTYPE html>
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
    </style>
</head>
<body>
    <div class="container">
        <div id="lottie-header"></div>
        <h1>Agent de Prospection</h1>
        <div id="messages"></div>
        <input id="prompt" type="text" placeholder="Posez votre question...">
        <button id="send">Envoyer</button>
    </div>

    <script>
        // Animations Lottie
        lottie.loadAnimation({
            container: document.getElementById("lottie-header"),
            renderer: "svg",
            loop: true,
            autoplay: true,
            path: "https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json"
        });

        // Chat basique
        document.getElementById("send").addEventListener("click", async () => {
            const prompt = document.getElementById("prompt").value;
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: prompt })
            });
            const data = await response.json();
            const msgDiv = document.createElement("div");
            msgDiv.className = "message";
            msgDiv.textContent = data.reply;
            document.getElementById("messages").appendChild(msgDiv);
        });
    </script>
</body>
</html>
"""
    return Response(html_content, mimetype="text/html")

# [Le reste de ton code existant...]

if __name__ == "__main__":
    ensure_schema()
    port = int(os.environ.get("PORT", "5000"))
    logger.info(f"Starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
