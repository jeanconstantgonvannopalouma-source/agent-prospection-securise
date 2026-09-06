import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent")

app = Flask(__name__)
CORS(app)

DATABASE_URL       = os.getenv("DATABASE_URL", "")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY", "")
SMTP_SERVER        = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT          = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER          = os.getenv("SMTP_USER", "")
SMTP_PASSWORD      = os.getenv("SMTP_PASSWORD", "")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./agent_prospection.db"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine       = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base         = declarative_base()

GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
    logger.info("Gemini configuré")
except Exception as e:
    logger.warning(f"Gemini non disponible: {e}")

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
        return
    cols = {c["name"] for c in insp.get_columns("prospects")}
    missing = []
    for col, typ in [
        ("company","VARCHAR(255)"),("job_title","VARCHAR(150)"),
        ("industry","VARCHAR(100)"),("country","VARCHAR(2)"),
        ("status","VARCHAR(50)"),("qualification_score","INTEGER"),
        ("notes","TEXT"),("created_at","TIMESTAMP"),("updated_at","TIMESTAMP")
    ]:
        if col not in cols:
            missing.append((col, typ))
    if missing:
        with engine.connect() as conn:
            for name, typ in missing:
                conn.execute(text(f"ALTER TABLE prospects ADD COLUMN {name} {typ}"))
            conn.commit()
    Base.metadata.create_all(engine)

ensure_schema()

def ask_gemini(prompt: str) -> str:
    if GEMINI_AVAILABLE:
        try:
            model    = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Erreur Gemini: {e}")
    return f"Bonjour ! Je suis ton agent de prospection pour Finance OS (12€) et Content Planner OS (12€). Comment puis-je vous aider ?"

def send_email_smtp(to_email: str, subject: str, body: str) -> bool:
    try:
        msg            = MIMEMultipart()
        msg["From"]    = SMTP_USER
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email envoyé à {to_email}")
        return True
    except Exception as e:
        logger.error(f"Erreur SMTP: {e}")
        return False

@app.before_request
def require_token():
    public = ["/", "/ui", "/health", "/api/chat", "/api/admin/chat", "/api/admin/stats", "/favicon.ico"]
    if request.path in public:
        return None
    if request.path.startswith("/static/"):
        return None
    if request.method == "OPTIONS":
        return None
    if not INTERNAL_API_TOKEN:
        return None
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {INTERNAL_API_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

@app.route("/")
def root():
    return jsonify({"service": "agent-prospection", "status": "online", "ui": "/ui"}), 200

@app.route("/health")
def health():
    try:
        db    = SessionLocal()
        count = db.query(Prospect).count()
        db.close()
        return jsonify({
            "status"          : "healthy",
            "database"        : "ok",
            "prospects_count" : count,
            "gemini"          : "ok" if GEMINI_AVAILABLE else "fallback",
            "smtp"            : "configured" if SMTP_USER else "missing"
        }), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route("/ui")
def ui():
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent de Prospection</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #0f172a, #1e3a5f); min-height: 100vh; color: white; }
        .container { width: min(1000px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0; }
        .header { display: flex; align-items: center; gap: 16px; margin-bottom: 30px; }
        #lottie-header { width: 80px; height: 80px; flex-shrink: 0; }
        .title h1 { font-size: 28px; color: white; }
        .title p { color: #dbeafe; margin-top: 5px; }
        .chat-box { background: rgba(255,255,255,0.95); border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; min-height: 500px; }
        .chat-header { padding: 20px; border-bottom: 1px solid #e2e8f0; }
        .chat-header h2 { color: #102a43; font-size: 18px; }
        .chat-header p { color: #64748b; font-size: 13px; margin-top: 5px; }
        #messages { flex: 1; overflow-y: auto; padding: 20px; background: #f8fafc; min-height: 350px; }
        .message { max-width: 80%; margin-bottom: 12px; padding: 12px 15px; border-radius: 12px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; animation: fadeIn 0.3s ease; }
        .user-msg { margin-left: auto; background: #2563eb; color: white; }
        .agent-msg { margin-right: auto; background: white; color: #1e293b; border: 1px solid #e2e8f0; }
        .typing { display: flex; gap: 5px; align-items: center; padding: 12px 15px; background: white; border: 1px solid #e2e8f0; border-radius: 12px; width: fit-content; margin-bottom: 12px; }
        .typing span { width: 8px; height: 8px; background: #2563eb; border-radius: 50%; animation: bounce 1.2s infinite; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce { 0%,80%,100% { transform: scale(0.8); opacity: 0.5; } 40% { transform: scale(1.2); opacity: 1; } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .chat-form { display: flex; gap: 10px; padding: 16px; border-top: 1px solid #e2e8f0; background: white; }
        #prompt { flex: 1; padding: 12px; border: 1px solid #cbd5e1; border-radius: 9px; font-size: 15px; outline: none; }
        #prompt:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.15); }
        #send { padding: 12px 20px; background: #2563eb; color: white; border: none; border-radius: 9px; font-size: 15px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        #send:hover { background: #1d4ed8; }
        #send:disabled { opacity: 0.5; cursor: not-allowed; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
        .stat { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; text-align: center; }
        .stat-value { font-size: 28px; font-weight: bold; color: #60a5fa; }
        .stat-label { font-size: 12px; color: #dbeafe; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div id="lottie-header"></div>
            <div class="title">
                <h1>Agent de Prospection</h1>
                <p>Interface privée de pilotage</p>
            </div>
        </div>
        <div class="stats">
            <div class="stat">
                <div class="stat-value" id="count-total">...</div>
                <div class="stat-label">Prospects total</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="count-new">...</div>
                <div class="stat-label">Nouveaux</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="count-contacted">...</div>
                <div class="stat-label">Contactés</div>
            </div>
        </div>
        <div class="chat-box">
            <div class="chat-header">
                <h2>Assistant de Prospection</h2>
                <p>Donne une instruction à ton agent (ex: Rédige un email pour Marc Vasseur)</p>
            </div>
            <div id="messages"></div>
            <form class="chat-form" id="chat-form">
                <input id="prompt" type="text" placeholder="Ex: Rédige un email pour vendre Finance OS à 12€..." autocomplete="off" required>
                <button id="send" type="submit">Envoyer</button>
            </form>
        </div>
    </div>
    <script>
        lottie.loadAnimation({ container: document.getElementById("lottie-header"), renderer: "svg", loop: true, autoplay: true, path: "https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json" });

        const messages = document.getElementById("messages");
        const form     = document.getElementById("chat-form");
        const input    = document.getElementById("prompt");
        const btn      = document.getElementById("send");

        function addMsg(role, text) {
            const d = document.createElement("div");
            d.className = "message " + (role === "user" ? "user-msg" : "agent-msg");
            d.textContent = text;
            messages.appendChild(d);
            messages.scrollTop = messages.scrollHeight;
        }

        function showTyping() {
            const t = document.createElement("div");
            t.className = "typing"; t.id = "typing";
            t.innerHTML = "<span></span><span></span><span></span>";
            messages.appendChild(t);
            messages.scrollTop = messages.scrollHeight;
        }

        function hideTyping() {
            const t = document.getElementById("typing");
            if (t) t.remove();
        }

        async function loadStats() {
            try {
                const r = await fetch("/api/admin/stats");
                const d = await r.json();
                document.getElementById("count-total").textContent     = d.prospects_count || 0;
                document.getElementById("count-new").textContent       = d.new_count || 0;
                document.getElementById("count-contacted").textContent = d.contacted_count || 0;
            } catch(e) {}
        }

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const msg = input.value.trim();
            if (!msg) return;
            addMsg("user", msg);
            input.value = "";
            btn.disabled = true;
            btn.textContent = "...";
            showTyping();
            try {
                const r = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: msg })
                });
                const d = await r.json();
                hideTyping();
                addMsg("agent", d.reply || d.error || "Erreur inconnue");
                loadStats();
            } catch(err) {
                hideTyping();
                addMsg("agent", "Erreur de connexion au serveur.");
            } finally {
                btn.disabled = false;
                btn.textContent = "Envoyer";
                input.focus();
            }
        });

        addMsg("agent", "Bonjour ! Je suis ton agent de prospection.\\n\\nJe peux:\\n→ Rédiger des emails personnalisés\\n→ Lister tes prospects\\n→ Préparer des campagnes\\n→ T\\'aider à vendre Finance OS (12€) et Content Planner OS (12€)\\n\\nQue veux-tu faire ?");
        loadStats();
    </script>
</body>
</html>"""
    return Response(html, mimetype="text/html")

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
        p = Prospect(
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
        db.add(p)
        db.commit()
        db.refresh(p)
        return jsonify({"status": "success", "id": p.id, "email": p.email}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route("/api/prospects", methods=["GET"])
def list_prospects():
    limit = min(int(request.args.get("limit", 50)), 200)
    db    = SessionLocal()
    try:
        rows = db.query(Prospect).order_by(Prospect.id.desc()).limit(limit).all()
        return jsonify({
            "count"     : len(rows),
            "prospects" : [
                {"id": r.id, "first_name": r.first_name, "last_name": r.last_name,
                 "email": r.email, "company": r.company, "job_title": r.job_title,
                 "industry": r.industry, "status": r.status}
                for r in rows
            ]
        }), 200
    finally:
        db.close()

@app.route("/api/prospects/<int:pid>", methods=["DELETE"])
def delete_prospect(pid):
    db = SessionLocal()
    try:
        p = db.query(Prospect).filter(Prospect.id == pid).first()
        if not p:
            return jsonify({"error": "Prospect non trouvé"}), 404
        db.delete(p)
        db.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route("/api/send-email", methods=["POST"])
def send_email_route():
    data    = request.get_json() or {}
    to      = data.get("to", "")
    subject = data.get("subject", "")
    body    = data.get("body", "")
    if not all([to, subject, body]):
        return jsonify({"error": "to, subject et body requis"}), 400
    success = send_email_smtp(to, subject, body)
    if success:
        return jsonify({"status": "success", "message": f"Email envoyé à {to}"}), 200
    else:
        return jsonify({"error": "Échec envoi email. Vérifiez SMTP_USER et SMTP_PASSWORD"}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json() or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message vide"}), 400
    db = SessionLocal()
    try:
        count    = db.query(Prospect).count()
        nouveaux = db.query(Prospect).filter(Prospect.status == "nouveau").count()
        derniers = db.query(Prospect).order_by(Prospect.id.desc()).limit(5).all()
        liste    = "\n".join([f"- {p.first_name} {p.last_name} | {p.email} | {p.company} | {p.status}" for p in derniers])
        prompt   = (
            f"Tu es un agent de prospection expert pour deux templates Notion :\n"
            f"1. Finance OS à 12€ (gestion budget, cashflow, finances)\n"
            f"2. Content Planner OS à 12€ (planification contenu réseaux sociaux)\n"
            f"Bundle des deux : 20€\n\n"
            f"Base de données : {count} prospects total, {nouveaux} nouveaux.\n"
            f"Derniers prospects :\n{liste}\n\n"
            f"Instruction : {message}\n\n"
            f"Réponds en français, de façon concise et professionnelle."
        )
        reply = ask_gemini(prompt)
        return jsonify({"reply": reply}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
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

@app.route("/api/admin/chat", methods=["POST"])
def admin_chat():
    data        = request.get_json() or {}
    instruction = (data.get("instruction") or "").strip()
    if not instruction:
        return jsonify({"error": "Instruction vide"}), 400
    db = SessionLocal()
    try:
        count    = db.query(Prospect).count()
        prospects = db.query(Prospect).order_by(Prospect.id.desc()).limit(20).all()
        liste    = "\n".join([
            f"- ID:{p.id} | {p.first_name} {p.last_name} | {p.email} | {p.company} | {p.job_title} | {p.industry} | {p.status}"
            for p in prospects
        ])
        prompt = (
            f"Tu es un agent de prospection expert.\n"
            f"Produits : Finance OS (12€), Content Planner OS (12€), Bundle (20€)\n"
            f"Base : {count} prospects.\n{liste}\n\n"
            f"Instruction : {instruction}\n\nRéponds en français."
        )
        answer = ask_gemini(prompt)
        return jsonify({"status": "success", "answer": answer, "prospects_count": count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    logger.info(f"Starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
