"""
SERVEUR WEB PROSPECTING AGENT - JEAN CONSTANT (MÉMOIRE & DEEP RESEARCH)
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
from modules.web_researcher import web_researcher

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

@app.route('/api/deep-research', methods=['POST'])
def deep_research_endpoint():
    payload = request.get_json() or {}
    target = payload.get("target", "payfit.com")
    result = web_researcher.deep_search_company(target)
    return jsonify({"success": True, "result": result})

@app.route('/api/knowledge-base', methods=['GET', 'POST'])
def kb_endpoint():
    if request.method == 'GET':
        return jsonify(knowledge_base.kb_data)
    else:
        payload = request.get_json() or {}
        knowledge_base.save_kb(payload)
        return jsonify({"success": True, "data": knowledge_base.kb_data})

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    payload = request.get_json() or {}
    user_msg = payload.get("message", "").strip()
    history = payload.get("history", [])

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return jsonify({"reply": "❌ Erreur: Clé GEMINI_API_KEY introuvable dans .env"})

    genai.configure(api_key=api_key)

    # Reconstruction de l'historique conversationnel pour Gemini
    history_context = "HISTORIQUE DE LA CONVERSATION EN COURS :\n"
    for item in history[-8:]: # Conserve les 8 derniers messages
        role_label = "Utilisateur" if item.get("role") == "user" else "Agent"
        history_context += f"{role_label}: {item.get('content')}\n"

    kb_context = knowledge_base.get_prompt_context()

    system_instruction = f"""
Tu es l'agent de prospection personnalisé de Jean Constant.

{kb_context}

INFORMATIONS SUR JEAN CONSTANT :
- Nom complet : Jean Constant Gonvanno Palouma
- E-mail officiel : jeanconstantgonvannopalouma@gmail.com
- Téléphone : +33 6 20 07 81 93

{history_context}

DIRECTIVES DE COMPORTEMENT :
- Utilise l'HISTORIQUE DE LA CONVERSATION ci-dessus pour comprendre le contexte des échanges précédents.
- Si l'utilisateur te demande de modifier, raccourcir ou adapter un message précédent, réfère-toi au message déjà généré dans l'historique.
- Si l'utilisateur te demande qui tu es, réponds : "Je suis l'agent de prospection personnalisé de Jean Constant."
- RÈGLES DE FORMATAGE STRICTES : N'utilise JAMAIS d'astérisques (* ou **), JAMAIS de lignes de séparation (*** ou ---). Texte ultra-propre et naturel.
"""
    full_prompt = f"{system_instruction}\n\nDERNIER MESSAGE DE L'UTILISATEUR : {user_msg}"

    # Envoi direct d'email si demandé avec adresse explicite
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
            
            send_res = email_sender.send_email(recipient, subject, body)
            if send_res.get("success"):
                return jsonify({"reply": f"✅ E-mail envoyé avec succès à {recipient} !\n\nObjet : {subject}\n\n{body}"})
        except Exception as e:
            pass

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
    print(f"\n🚀 SERVEUR V28.0 (MÉMOIRE & DEEP SEARCH) EN LIGNE SUR http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
