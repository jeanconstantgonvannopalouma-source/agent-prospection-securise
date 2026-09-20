"""
SERVEUR WEB PROSPECTING AGENT - JEAN CONSTANT (AUTONOMIE TOTALE SUR LIEN)
"""
import os
import sys
import warnings
import re

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
from modules.revenue_autonomy_engine import revenue_autonomy_engine

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

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    payload = request.get_json() or {}
    user_msg = payload.get("message", "").strip()

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return jsonify({"reply": "❌ Erreur: Clé GEMINI_API_KEY introuvable."})

    genai.configure(api_key=api_key)

    # 1. DÉTECTION D'URL ET DÉCLENCHEMENT DE LA CAMPAGNE AUTONOME TOTALE
    url_match = re.search(r'https?://[^\s]+|www\.[^\s]+', user_msg)
    if url_match:
        target_url = url_match.group(0)
        print(f"🚀 URL Reçue : {target_url} -> DÉCLENCHEMENT DU DÉPLOIEMENT AUTONOME COMPLET...")
        autonomy_report = revenue_autonomy_engine.execute_full_autonomous_campaign(target_url)
        return jsonify({"reply": autonomy_report})

    # 2. DÉTECTION D'ORDRE D'ENVOI D'EMAIL INDIVIDUEL
    msg_lower = user_msg.lower()
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_msg)
    if ("envoie" in msg_lower or "envoyer" in msg_lower or "écris" in msg_lower) and email_match:
        recipient = email_match.group(0)
        try:
            m = genai.GenerativeModel("gemini-3.6-flash")
            draft = m.generate_content(f"Rédige un e-mail professionnel pour {recipient} sur la consigne : '{user_msg}'. Sans astérisques.").text.strip().replace("***", "").replace("**", "")
            lines = draft.split("\n")
            subject = lines[0].replace("Objet :", "").strip() if len(lines) > 1 else "Message de Jean Constant"
            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else draft
            
            send_res = email_sender.send_email(recipient, subject, body, prospect_name="Prospect")
            if send_res.get("success"):
                return jsonify({"reply": f"✅ E-mail envoyé avec succès à {recipient} !\n\nObjet : {subject}\n\n{body}"})
        except Exception:
            pass

    # 3. CHAT CONVERSATIONNEL STANDARD
    kb_context = knowledge_base.get_prompt_context()

    system_instruction = f"""
Tu es l'agent de prospection personnalisé de Jean Constant Gonvanno Palouma.

{kb_context}

INFORMATIONS SUR JEAN CONSTANT :
- Nom complet : Jean Constant Gonvanno Palouma
- E-mail officiel : jeanconstantgonvannopalouma@gmail.com
- Téléphone : +33 6 20 07 81 93

DIRECTIVES :
- Si l'utilisateur te transmet un lien URL, lance immédiatement la campagne automatique de prospection.
- Si l'utilisateur te demande qui tu es, réponds : "Je suis l'agent de prospection personnalisé de Jean Constant Gonvanno Palouma."
- ZERO PARASITE : N'utilise JAMAIS d'astérisques (* ou **), JAMAIS de lignes de séparation (*** ou ---).
"""
    full_prompt = f"{system_instruction}\n\nUTILISATEUR : {user_msg}"

    for model_name in VALID_CHAT_MODELS:
        if not model_name: continue
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(full_prompt)
            clean_reply = response.text.replace("***", "").replace("**", "").replace("---", "==================================================")
            return jsonify({"reply": clean_reply.strip(), "active_model": model_name})
        except Exception:
            continue

    return jsonify({"reply": "⚠️ Tous les modèles Gemini sont temporairement indisponibles."})

if __name__ == '__main__':
    print(f"\n🚀 SERVEUR D'AUTONOMIE TOTALE EN LIGNE SUR http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
