"""
SERVEUR WEB PROSPECTING AGENT - JEAN CONSTANT V30.0
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

@app.route('/api/inbox/check', methods=['GET'])
def check_inbox_endpoint():
    try:
        emails = email_assistant.fetch_recent_inbox_emails(count=5)
        return jsonify({"success": True, "emails": emails})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    try:
        payload = request.get_json() or {}
        user_msg = payload.get("message", "").strip()

        if not user_msg:
            return jsonify({"reply": "Veuillez entrer un message."})

        msg_lower = user_msg.lower()

        # A. INTERCEPTION EXPLICITE DES DEMANDES SUR L'ÉTAT DE LA BOÎTE MAIL
        inbox_keywords = ["boite mail", "boîte mail", "état de ma", "mes mails", "derniers mails", "reçu des mails", "inbox", "réception"]
        if any(kw in msg_lower for k in inbox_keywords for kw in [k]):
            recent_emails = email_assistant.fetch_recent_inbox_emails(count=5)
            reply = "📬 ÉTAT ACTUEL DE TA BOÎTE GMAIL (jeanconstantgonvannopalouma@gmail.com) :\n\n"
            if recent_emails:
                for idx, em in enumerate(recent_emails, 1):
                    reply += f"{idx}. De : {em['sender_name']} ({em['from']})\n   Objet : {em['subject']}\n   Extrait : '{em['snippet']}'\n\n"
                reply += "==================================================\n"
                reply += "Je suis connecté à ta boîte mail 24h/24. Tu peux me demander d'envoyer un mail à un contact ou d'y répondre !"
            else:
                reply += "Ta boîte mail est actuellement propre (aucun nouveau message non lu).\n\nJe suis prêt à expédier tes prochaines campagnes !"
            return jsonify({"reply": reply})

        # B. INTERCEPTION DES LIENS URL (ANALYSE & PLAN DE MONÉTISATION IMMÉDIAT)
        url_match = re.search(r'https?://[^\s]+|www\.[^\s]+', user_msg)
        if url_match:
            target_url = url_match.group(0)
            print(f"🎯 URL Détectée : {target_url} -> Analyse financière en cours...")
            analysis_reply = revenue_autonomy_engine.analyze_and_plan_campaign(target_url)
            return jsonify({"reply": analysis_reply})

        # C. INTERCEPTION D'ORDRE D'ENVOI D'EMAIL
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_msg)
        if ("envoie" in msg_lower or "envoyer" in msg_lower or "écris" in msg_lower) and email_match:
            recipient = email_match.group(0)
            subj = "Message de Jean Constant Gonvanno Palouma"
            body = f"Bonjour,\n\nJe fais suite à notre contact concernant vos enjeux de croissance B2B.\n\nAuriez-vous une disponibilité cette semaine pour un rapide point ?\n\nBien à vous,\nJean Constant Gonvanno Palouma\n+33 6 20 07 81 93"
            
            send_res = email_sender.send_email(recipient, subj, body, prospect_name="Prospect")
            if send_res.get("success"):
                return jsonify({"reply": f"✅ E-mail rédigé et envoyé avec succès à {recipient} !\n\nObjet : {subj}\n\n{body}"})
            else:
                return jsonify({"reply": f"❌ Échec de l'envoi à {recipient} : {send_res.get('error')}"})

        # D. TRAITEMENT CHATBOT GEMINI STANDARD
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return jsonify({"reply": "❌ Erreur: Clé GEMINI_API_KEY introuvable."})

        genai.configure(api_key=api_key)
        kb_context = knowledge_base.get_prompt_context()

        system_instruction = f"""
Tu es l'agent de prospection personnalisé de Jean Constant Gonvanno Palouma.

{kb_context}

INFORMATIONS EXACTES SUR JEAN CONSTANT :
- Nom complet : Jean Constant Gonvanno Palouma
- E-mail officiel : jeanconstantgonvannopalouma@gmail.com
- Téléphone : +33 6 20 07 81 93

DIRECTIVES :
- Tu ES connecté à sa boîte mail (jeanconstantgonvannopalouma@gmail.com). Ne dis JAMAIS le contraire.
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
                return jsonify({"reply": clean_reply.strip()})
            except Exception:
                continue

        return jsonify({"reply": "⚠️ Tous les modèles Gemini sont temporairement indisponibles."})

    except Exception as err:
        print(f"❌ Erreur sur /api/chat : {err}")
        return jsonify({"reply": f"⚠️ Une erreur est survenue lors du traitement : {str(err)}"})

if __name__ == '__main__':
    print(f"\n🚀 SERVEUR V30.0 EN LIGNE SUR http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
