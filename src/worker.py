import os
import time
import logging
import smtplib
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("autopilot")

DATABASE_URL   = os.getenv("DATABASE_URL", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "TA_CLE_GEMINI_ICI")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
DRY_RUN        = os.getenv("AUTOPILOT_DRY_RUN", "True").lower() == "true"
BATCH_SIZE     = int(os.getenv("AUTOPILOT_BATCH_SIZE", "5"))
SLEEP_SECONDS  = int(os.getenv("AUTOPILOT_SLEEP_SECONDS", "30"))
SMTP_SERVER    = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT      = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER      = os.getenv("SMTP_USER", "")
SMTP_PASSWORD  = os.getenv("SMTP_PASSWORD", "")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

genai.configure(api_key=GEMINI_API_KEY)

Base         = declarative_base()
engine       = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

class Prospect(Base):
    __tablename__ = "prospects"
    id        = Column(Integer, primary_key=True)
    first_name= Column(String(100))
    last_name = Column(String(100))
    email     = Column(String(255), unique=True)
    company   = Column(String(255))
    job_title = Column(String(150))
    industry  = Column(String(100))
    status    = Column(String(50), default="nouveau")
    notes     = Column(Text)
    created_at= Column(DateTime, default=datetime.utcnow)

def generate_email(prospect) -> dict:
    """Génère un email personnalisé avec Gemini"""
    try:
        model  = genai.GenerativeModel(GEMINI_MODEL)
        prompt = (
            f"Tu es un expert en prospection pour 'Finance OS', un template Notion à 19€.\n"
            f"Rédige un email de prospection court (max 100 mots) et personnalisé pour :\n"
            f"- Prénom : {prospect.first_name}\n"
            f"- Entreprise : {prospect.company or 'son activité'}\n"
            f"- Poste : {prospect.job_title or 'Professionnel'}\n"
            f"- Secteur : {prospect.industry or 'Indépendant'}\n\n"
            f"Format de réponse OBLIGATOIRE :\n"
            f"OBJET: [sujet de l'email]\n"
            f"CORPS: [corps de l'email]\n\n"
            f"Email chaleureux, direct, une seule action demandée (voir un aperçu)."
        )
        response = model.generate_content(prompt)
        raw      = response.text

        subject = f"Idée rapide pour {prospect.company or prospect.first_name}"
        body    = raw

        if "OBJET:" in raw and "CORPS:" in raw:
            subject = raw.split("OBJET:")[1].split("CORPS:")[0].strip()
            body    = raw.split("CORPS:")[1].strip()

        return {"subject": subject, "body": body}

    except Exception as e:
        logger.warning(f"Gemini error, fallback template: {e}")
        return {
            "subject": f"Idée rapide pour {prospect.company or prospect.first_name}",
            "body": (
                f"Bonjour {prospect.first_name},\n\n"
                f"Je me permets de vous contacter car {prospect.company or 'votre activité'} "
                f"pourrait bénéficier de Finance OS, un template Notion à 19€ pour suivre "
                f"budget, cashflow et prévisions facilement.\n\n"
                f"Est-ce que je peux vous envoyer un aperçu ?\n\n"
                f"Cordialement"
            )
        }

def send_email(to_email: str, subject: str, body: str):
    """Envoie un email via SMTP Gmail"""
    msg            = MIMEMultipart()
    msg['From']    = SMTP_USER
    msg['To']      = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

def run():
    logger.info(f"🚀 Autopilot démarré | DRY_RUN={DRY_RUN} | BATCH={BATCH_SIZE}")

    while True:
        db = SessionLocal()
        try:
            prospects = db.query(Prospect).filter(
                Prospect.status == "nouveau"
            ).limit(BATCH_SIZE).all()

            if not prospects:
                logger.info("💤 Aucun prospect nouveau. Attente...")
                time.sleep(SLEEP_SECONDS)
                continue

            logger.info(f"📋 {len(prospects)} prospects à traiter | DRY_RUN={DRY_RUN}")

            for p in prospects:
                try:
                    email_data = generate_email(p)
                    subject    = email_data["subject"]
                    body       = email_data["body"]

                    if DRY_RUN:
                        logger.info(f"🧪 [DRY_RUN] Would send to {p.email} | subject='{subject}'")
                    else:
                        send_email(p.email, subject, body)
                        logger.info(f"✅ Email envoyé à {p.email} | subject='{subject}'")

                    p.status = "contacté"
                    db.commit()
                    time.sleep(2)

                except Exception as e:
                    logger.error(f"❌ Erreur pour {p.email}: {e}")
                    db.rollback()

        except Exception as e:
            logger.error(f"💥 Erreur boucle principale: {e}")
        finally:
            db.close()

        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    run()
