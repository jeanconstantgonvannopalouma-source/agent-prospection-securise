import os
import logging
from flask import Flask, jsonify, Response, request

# Configuration initiale
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # CORRECTION: logger bien défini

app = Flask(__name__)

# Configuration Gemini (avec gestion d'erreur complète)
GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    logger.info("✅ Gemini configuré avec succès")
except ImportError:
    logger.warning("⚠️ Module google.generativeai non disponible")
except Exception as e:
    logger.error(f"❌ Erreur Gemini: {e}")

# Route racine
@app.route("/")
def root():
    return jsonify({
        "service": "agent-prospection",
        "status": "online",
        "gemini": "available" if GEMINI_AVAILABLE else "unavailable"
    })

# Route de santé
@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

# Interface UI
@app.route("/ui")
def ui():
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Agent de Prospection</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <style>
        body { font-family: Arial; background: #0f172a; color: white; padding: 20px; }
        #lottie-header { width: 100px; height: 100px; }
        .message { background: white; color: black; padding: 10px; margin: 5px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Agent de Prospection</h1>
    <div id="lottie-header"></div>
    <div id="messages"></div>
    <input id="prompt" placeholder="Posez votre question...">
    <button id="send">Envoyer</button>

    <script>
        lottie.loadAnimation({
            container: document.getElementById("lottie-header"),
            renderer: "svg",
            loop: true,
            autoplay: true,
            path: "https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json"
        });

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
</html>"""
    return Response(html_content, mimetype="text/html")

# Route de chat avec FALLBACK COMPLET
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message vide"}), 400

    # Réponses fallback (toujours disponibles)
    fallback_responses = {
        "bonjour": "Bonjour ! Comment puis-je vous aider avec Finance OS ?",
        "combien": "Il y a actuellement des prospects dans la base.",
        "liste": "Voici quelques prospects : Marc Vasseur, Julie Faure...",
        "default": f"Voici une réponse pour : {message}"
    }

    # Essaye Gemini si disponible
    if GEMINI_AVAILABLE:
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(f"Réponds en français: {message}")
            return jsonify({"reply": response.text}), 200
        except Exception as e:
            logger.error(f"Erreur Gemini: {e}")

    # Utilise le fallback
    for keyword, response in fallback_responses.items():
        if keyword in message.lower():
            return jsonify({"reply": response}), 200

    return jsonify({"reply": fallback_responses["default"]}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    logger.info(f"Démarrage sur le port {port}")
    app.run(host="0.0.0.0", port=port)
