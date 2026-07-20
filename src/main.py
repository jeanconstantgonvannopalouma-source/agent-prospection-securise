import os
import logging
import google.generativeai as genai  # ← Ancien package (à garder pour l'instant)
from flask import Flask, jsonify, Response, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration Gemini (avec gestion d'erreur)
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY manquante dans les variables d'environnement")

    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini configuré avec succès")
except Exception as e:
    logger.error(f"Erreur Gemini: {e}")

@app.route("/api/chat", methods=["POST"])
def chat():
    """Route de chat avec gestion d'erreur complète"""
    try:
        data = request.get_json() or {}
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "Message vide"}), 400

        # Utilisation d'un modèle qui existe SÛREMENT
        model = genai.GenerativeModel("gemini-pro")  # ← Changé de gemini-1.5-flash à gemini-pro
        response = model.generate_content(f"Réponds à cette question: {message}")

        return jsonify({"reply": response.text}), 200

    except Exception as e:
        logger.error(f"Erreur chat: {e}")
        return jsonify({
            "error": "Erreur interne",
            "details": str(e),
            "help": "Vérifiez votre clé API Gemini et le modèle utilisé"
        }), 500

# [Le reste de ton code...]
