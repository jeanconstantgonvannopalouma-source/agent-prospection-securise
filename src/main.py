import os
import logging
from flask import Flask, jsonify, Response, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration Gemini (avec fallback)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    logger.info("✅ Gemini configuré")
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("⚠️ Gemini non disponible - mode fallback activé")

# [Le reste de ton code existant...]

@app.route("/api/chat", methods=["POST"])
def chat():
    """Route de chat avec fallback si Gemini échoue"""
    data = request.get_json() or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message vide"}), 400

    if GEMINI_AVAILABLE:
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(f"Réponds en français: {message}")
            return jsonify({"reply": response.text}), 200
        except Exception as e:
            logger.error(f"Erreur Gemini: {e}")
            # Fallback si Gemini échoue

    # FALLBACK SI GEMINI N'EST PAS DISPONIBLE
    fallback_responses = {
        "bonjour": "Bonjour ! Comment puis-je vous aider avec Finance OS ?",
        "combien": "Il y a actuellement X prospects dans la base.",
        "liste": "Voici quelques prospects : Marc Vasseur, Julie Faure...",
        "default": "Je suis en mode fallback. Voici une réponse générique pour : " + message
    }

    for keyword, response in fallback_responses.items():
        if keyword in message.lower():
            return jsonify({"reply": response}), 200

    return jsonify({"reply": fallback_responses["default"]}), 200

# [Le reste de ton code UI et API...]
