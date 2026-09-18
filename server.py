"""
SERVEUR WEB PROSPECTING AGENT - JEAN CONSTANT GONVANNO PALOUMA
"""
import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.abspath("src"))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai

from core.agent import agent
from modules.db_adapter import db_adapter
from modules.knowledge_base import knowledge_base
from modules.email_assistant import email_assistant
from modules.email_sender import email_sender

app = Flask(__name__, template_folder='templates')
CORS(app)

PORT = int(os.getenv("PORT", "5001"))

VALID_CHAT_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest"
]

@app.route('/')
@app.route('/ui')
@app.route('/dashboard')
def render_ui():
    return render_template('index.html')

@app.route('/api/inbox/check', methods=['GET'])
def check_inbox_endpoint():
    emails = email_assistant.fetch_recent_inbox_emails(count=5)
    return jsonify({"success": True, "emails": emails})

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    payload = request.get_json() or {}
    user_msg = payload.get("message", "").strip()

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return jsonify({"reply": "❌ Erreur: Clé GEMINI_API_KEY introuvable."})

    genai.configure(api_key=api_key)

    recent_emails = email_assistant.fetch_recent_inbox_emails(count=5)
    stats = db_adapter.get_stats()
    recent_contacts = stats.get("recent_prospects", [])

    inbox_context_text = "MESSAGES DANS TA BOÎTE GMAIL (jeanconstantgonvannopalouma@gmail.com) :\n"
    for idx, em in enumerate(recent_emails, 1):
        inbox_context_text += f"{idx}. De: {em['sender_name']} ({em['from']}) | Objet: {em['subject']}\n"

    crm_context_text = "\nCONTACTS CRM DISPONIBLES :\n"
    for c in recent_contacts:
        crm_context_text += f"- {c.get('first_name')} ({c.get('company')}) -> Email: {c.get('email')}\n"

    msg_lower = user_msg.lower()
    if "envoie un mail à" in msg_lower or "envoyer un mail à" in msg_lower or "écris un mail à" in msg_lower:
        target_query = user_msg.replace("envoie un mail à", "").replace("envoyer un mail à", "").replace("écris un mail à", "").strip()
        contact = email_assistant.resolve_contact_email(target_query.split()[0])
        
        target_email = contact.get("email") if contact else None
        target_name = contact.get("first_name") if contact else target_query.split()[0]

        if target_email:
            subj = f"Échange concernant {contact.get('company', 'votre projet')}"
            body = f"Bonjour {target_name},\n\nJe fais suite à nos récents échanges concernant vos enjeux de croissance. Auriez-vous une disponibilité cette semaine pour un rapide point ?\n\nBien à vous,\nJean Constant Gonvanno Palouma\n+33 6 20 07 81 93"
            
            send_res = email_sender.send_email(target_email, subj, body, prospect_name=target_name)
            return jsonify({
                "reply": f"✅ EMAIL RÉDIGÉ ET ENVOYÉ À {target_name} ({target_email}) !\n\nObjet : {subj}\n\n{body}"
            })

    kb_context = knowledge_base.get_prompt_context()

    system_instruction = f"""
Tu es l'agent de prospection personnalisé de Jean Constant Gonvanno Palouma.

{kb_context}

INFORMATIONS EXACTES SUR JEAN CONSTANT GONVANNO PALOUMA :
- Son nom complet : Jean Constant Gonvanno Palouma
- Son adresse e-mail officielle : jeanconstantgonvannopalouma@gmail.com
- Son téléphone : +33 6 20 07 81 93

{inbox_context_text}
{crm_context_text}

DIRECTIVES DE COMPORTEMENT :
- Si l'utilisateur te demande quelle est son adresse e-mail, réponds TOUJOURS : "Ton adresse e-mail officielle est jeanconstantgonvannopalouma@gmail.com".
- Si l'utilisateur te demande son numéro de téléphone, réponds : "+33 6 20 07 81 93".
- Si l'utilisateur te demande qui tu es, réponds : "Je suis l'agent de prospection personnalisé de Jean Constant Gonvanno Palouma."
- N'utilise JAMAIS d'astérisques (* ou **), JAMAIS de lignes de séparation (*** ou ---). Texte ultra-propre et direct.
"""
    full_prompt = f"{system_instruction}\n\nUTILISATEUR : {user_msg}"

    for model_name in VALID_CHAT_MODELS:
        if not model_name: continue
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(full_prompt)
            clean_reply = response.text.replace("***", "").replace("---", "==================================================")
            return jsonify({"reply": clean_reply.strip(), "active_model": model_name})
        except Exception:
            continue

    return jsonify({"reply": "⚠️ Tous les modèles Gemini sont temporairement indisponibles."})

if __name__ == '__main__':
    print(f"\n🚀 SERVEUR CONNECTÉ A GMAIL (jeanconstantgonvannopalouma@gmail.com) EN LIGNE SUR http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
