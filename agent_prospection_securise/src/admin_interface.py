import os
import hmac

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)

admin_bp = Blueprint("admin", __name__)


LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Connexion - Agent de Prospection</title>
    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Arial, Helvetica, sans-serif;
            background-image:
                linear-gradient(rgba(5, 15, 35, 0.72), rgba(5, 15, 35, 0.82)),
                url("/static/background.jpg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }

        .login-card {
            width: min(420px, calc(100% - 32px));
            padding: 36px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 16px 45px rgba(0, 0, 0, 0.35);
        }

        h1 { margin: 0 0 10px; color: #102a43; font-size: 26px; }
        p  { margin: 0 0 25px; color: #52616b; line-height: 1.5; }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #243b53;
        }

        input {
            width: 100%;
            padding: 13px;
            border: 1px solid #cbd5e1;
            border-radius: 9px;
            font-size: 16px;
            outline: none;
        }

        input:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }

        button {
            width: 100%;
            margin-top: 18px;
            padding: 13px;
            border: 0;
            border-radius: 9px;
            color: white;
            background: #2563eb;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover { background: #1d4ed8; }

        .error {
            margin-top: 16px;
            padding: 10px;
            border-radius: 8px;
            color: #991b1b;
            background: #fee2e2;
        }

        .footer {
            margin-top: 22px;
            color: #64748b;
            font-size: 12px;
            text-align: center;
        }
    </style>
</head>
<body>
    <main class="login-card">
        <h1>Agent de Prospection</h1>
        <p>Connecte-toi pour accéder à ton interface d'administration.</p>

        <form method="POST" action="/login">
            <label for="password">Mot de passe administrateur</label>
            <input
                id="password"
                name="password"
                type="password"
                placeholder="Ton mot de passe"
                autocomplete="current-password"
                required
                autofocus
            >
            <button type="submit">Se connecter</button>
        </form>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        <div class="footer">Accès privé et sécurisé.</div>
    </main>
</body>
</html>
"""


ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Agent de Prospection</title>

    <!-- ← AJOUT : Lottie player chargé depuis CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>

    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, Helvetica, sans-serif;
            color: #172033;
            background-image:
                linear-gradient(rgba(5, 15, 35, 0.68), rgba(5, 15, 35, 0.85)),
                url("/static/background.jpg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }

        .container {
            width: min(1100px, calc(100% - 32px));
            margin: 0 auto;
            padding: 32px 0;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 25px;
        }

        /* ← AJOUT : zone titre + animation côte à côte */
        .topbar-left {
            display: flex;
            align-items: center;
            gap: 18px;
        }

        /* ← AJOUT : conteneur de l'animation Lottie dans le header */
        #lottie-header {
            width: 90px;
            height: 90px;
            flex-shrink: 0;
            filter: drop-shadow(0 0 12px rgba(99, 179, 237, 0.55));
        }

        .title h1 {
            margin: 0;
            color: white;
            font-size: 30px;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
        }

        .title p {
            margin: 7px 0 0;
            color: #dbeafe;
        }

        .logout {
            display: inline-block;
            padding: 10px 14px;
            border-radius: 8px;
            color: white;
            background: rgba(255, 255, 255, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.28);
            text-decoration: none;
            font-weight: bold;
        }

        .logout:hover { background: rgba(255, 255, 255, 0.28); }

        .layout {
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 20px;
        }

        .panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.25);
        }

        .sidebar {
            padding: 22px;
            height: fit-content;
        }

        .sidebar h2 {
            margin: 0 0 16px;
            font-size: 19px;
            color: #102a43;
        }

        /* ← AJOUT : animation Lottie dans la sidebar */
        #lottie-sidebar {
            width: 100%;
            height: 180px;
            margin-bottom: 18px;
            border-radius: 12px;
            overflow: hidden;
            background: linear-gradient(135deg, #0f172a, #1e3a5f);
        }

        .stat {
            padding: 14px;
            margin-bottom: 12px;
            border-radius: 10px;
            background: #eff6ff;
        }

        .stat-label { color: #52616b; font-size: 13px; }

        .stat-value {
            margin-top: 5px;
            color: #1d4ed8;
            font-size: 28px;
            font-weight: bold;
        }

        /* ← AJOUT : compteurs animés */
        .stat-value.counting {
            animation: countPulse 0.3s ease-out;
        }

        @keyframes countPulse {
            0%   { transform: scale(1.15); color: #059669; }
            100% { transform: scale(1);    color: #1d4ed8; }
        }

        .security-note {
            margin-top: 18px;
            padding: 13px;
            border-radius: 10px;
            color: #7c2d12;
            background: #ffedd5;
            font-size: 13px;
            line-height: 1.45;
        }

        .chat-panel {
            min-height: 650px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            padding: 20px 22px;
            border-bottom: 1px solid #e2e8f0;
        }

        .chat-header h2 { margin: 0; color: #102a43; font-size: 20px; }
        .chat-header p  { margin: 7px 0 0; color: #64748b; font-size: 14px; }

        #messages {
            flex: 1;
            overflow-y: auto;
            padding: 22px;
            background: rgba(248, 250, 252, 0.72);
        }

        .message {
            max-width: 82%;
            margin-bottom: 14px;
            padding: 13px 15px;
            border-radius: 12px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;

            /* ← AJOUT : apparition douce des messages */
            animation: fadeSlide 0.25s ease-out;
        }

        /* ← AJOUT : animation d'apparition */
        @keyframes fadeSlide {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0);   }
        }

        .assistant-message {
            margin-right: auto;
            color: #1e293b;
            background: white;
            border: 1px solid #e2e8f0;
        }

        .user-message {
            margin-left: auto;
            color: white;
            background: #2563eb;
        }

        .system-message {
            margin-right: auto;
            color: #7c2d12;
            background: #ffedd5;
            border: 1px solid #fed7aa;
        }

        /* ← AJOUT : indicateur "agent en train de réfléchir" */
        .typing-indicator {
            display: flex;
            gap: 5px;
            align-items: center;
            padding: 12px 15px;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            width: fit-content;
            margin-bottom: 14px;
        }

        .typing-indicator span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #2563eb;
            animation: bounce 1.2s infinite;
        }

        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40%            { transform: scale(1.2); opacity: 1;   }
        }

        .chat-form {
            display: flex;
            gap: 10px;
            padding: 18px;
            border-top: 1px solid #e2e8f0;
            background: white;
        }

        #prompt {
            flex: 1;
            min-width: 0;
            padding: 13px;
            border: 1px solid #cbd5e1;
            border-radius: 9px;
            font-size: 15px;
            outline: none;
        }

        #prompt:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }

        #send-button {
            padding: 13px 18px;
            border: 0;
            border-radius: 9px;
            color: white;
            background: #2563eb;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }

        #send-button:hover    { background: #1d4ed8; }
        #send-button:disabled { opacity: 0.55; cursor: not-allowed; }

        .examples {
            padding: 0 22px 18px;
            color: #64748b;
            background: white;
            font-size: 12px;
        }

        @media (max-width: 800px) {
            .container { width: min(100% - 20px, 1100px); padding: 18px 0; }

            .layout { grid-template-columns: 1fr; }

            .sidebar {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }

            .sidebar h2,
            .security-note,
            #lottie-sidebar { grid-column: 1 / -1; }

            .stat { margin: 0; }

            .chat-panel  { min-height: 580px; }
            .topbar      { align-items: flex-start; }
            .title h1    { font-size: 24px; }

            /* ← AJOUT responsive : animation header plus petite */
            #lottie-header { width: 60px; height: 60px; }
        }
    </style>
</head>

<body>
    <main class="container">

        <header class="topbar">

            <!-- ← AJOUT : wrapper gauche avec animation + titre -->
            <div class="topbar-left">

                <!-- ← AJOUT : animation Lottie dans le header -->
                <div id="lottie-header"></div>

                <div class="title">
                    <h1>Agent de Prospection</h1>
                    <p>Interface privée de pilotage et de validation.</p>
                </div>
            </div>

            <a class="logout" href="/logout">Déconnexion</a>
        </header>

        <section class="layout">

            <aside class="panel sidebar">
                <h2>Tableau de bord</h2>

                <!-- ← AJOUT : animation Lottie dashboard dans la sidebar -->
                <div id="lottie-sidebar"></div>

                <div class="stat">
                    <div class="stat-label">Prospects enregistrés</div>
                    <div class="stat-value" id="prospect-count">...</div>
                </div>

                <div class="stat">
                    <div class="stat-label">Mode actuel</div>
                    <div class="stat-value" style="font-size: 17px;">
                        Validation manuelle
                    </div>
                </div>

                <div class="security-note">
                    Les actions sensibles, notamment l'envoi d'emails,
                    devront être confirmées avant leur exécution.
                </div>
            </aside>

            <section class="panel chat-panel">

                <div class="chat-header">
                    <h2>Assistant de prospection</h2>
                    <p>Écris une instruction ou pose une question à ton agent.</p>
                </div>

                <div id="messages"></div>

                <form id="chat-form" class="chat-form">
                    <input
                        id="prompt"
                        type="text"
                        placeholder="Exemple : Combien de prospects ai-je ?"
                        autocomplete="off"
                        required
                    >
                    <button id="send-button" type="submit">Envoyer</button>
                </form>

                <div class="examples">
                    Exemples futurs :
                    « Ajoute Jean Dupont, jean@entreprise.fr »
                    · « Liste les prospects nouveaux »
                    · « Prépare une campagne pour le secteur informatique »
                </div>

            </section>
        </section>
    </main>

    <script>
        // ─────────────────────────────────────────────
        // ← AJOUT : Chargement des animations Lottie
        // Animation dashboard analytique (LottieFiles public)
        // ─────────────────────────────────────────────

        // Petite icône animée dans le header (graphique / analytics)
        lottie.loadAnimation({
            container : document.getElementById("lottie-header"),
            renderer  : "svg",
            loop      : true,
            autoplay  : true,
            path      : "https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json"
        });

        // Grande animation dashboard dans la sidebar
        lottie.loadAnimation({
            container : document.getElementById("lottie-sidebar"),
            renderer  : "svg",
            loop      : true,
            autoplay  : true,
            path      : "https://assets9.lottiefiles.com/packages/lf20_xlmz9xwm.json"
        });

        // ─────────────────────────────────────────────
        // Logique du chat (inchangée + typing indicator)
        // ─────────────────────────────────────────────

        const messages      = document.getElementById("messages");
        const form          = document.getElementById("chat-form");
        const promptInput   = document.getElementById("prompt");
        const sendButton    = document.getElementById("send-button");
        const prospectCount = document.getElementById("prospect-count");

        function addMessage(role, content) {
            const element = document.createElement("div");
            element.classList.add("message");

            if (role === "user")         element.classList.add("user-message");
            else if (role === "system")  element.classList.add("system-message");
            else                         element.classList.add("assistant-message");

            element.textContent = content;
            messages.appendChild(element);
            messages.scrollTop = messages.scrollHeight;
        }

        // ← AJOUT : affiche les 3 points "en train d'écrire"
        function showTyping() {
            const el = document.createElement("div");
            el.classList.add("typing-indicator");
            el.id = "typing";
            el.innerHTML = "<span></span><span></span><span></span>";
            messages.appendChild(el);
            messages.scrollTop = messages.scrollHeight;
        }

        // ← AJOUT : retire l'indicateur
        function hideTyping() {
            const el = document.getElementById("typing");
            if (el) el.remove();
        }

        async function refreshStats() {
            try {
                const response = await fetch("/api/admin/stats");
                if (!response.ok) return;
                const data = await response.json();

                // ← AJOUT : animation du compteur
                prospectCount.classList.remove("counting");
                void prospectCount.offsetWidth; // reflow
                prospectCount.classList.add("counting");
                prospectCount.textContent = data.prospects_count;

            } catch (error) {
                prospectCount.textContent = "?";
            }
        }

        form.addEventListener("submit", async function(event) {
            event.preventDefault();

            const instruction = promptInput.value.trim();
            if (!instruction) return;

            addMessage("user", instruction);
            promptInput.value    = "";
            promptInput.disabled = true;
            sendButton.disabled  = true;
            sendButton.textContent = "Envoi...";

            // ← AJOUT : affiche typing pendant la requête
            showTyping();

            try {
                const response = await fetch("/api/admin/chat", {
                    method  : "POST",
                    headers : { "Content-Type": "application/json" },
                    body    : JSON.stringify({ instruction })
                });

                const data = await response.json();
                hideTyping(); // ← AJOUT

                if (!response.ok) {
                    addMessage("system", data.error || "Une erreur est survenue.");
                    return;
                }

                addMessage("assistant", data.answer);
                refreshStats();

            } catch (error) {
                hideTyping(); // ← AJOUT
                addMessage(
                    "system",
                    "Impossible de contacter le serveur. Réessaie dans quelques instants."
                );
            } finally {
                promptInput.disabled   = false;
                sendButton.disabled    = false;
                sendButton.textContent = "Envoyer";
                promptInput.focus();
            }
        });

        addMessage(
            "assistant",
            "Bonjour. Je suis prêt à recevoir tes instructions.\\n\\n" +
            "Pour le moment, je peux confirmer la connexion et compter les prospects. " +
            "Nous ajouterons ensuite les actions réelles : ajout de prospects, campagnes, brouillons et validation d'envoi."
        );

        refreshStats();
    </script>
</body>
</html>
"""


# ─── Routes (inchangées) ───────────────────────────────────────────────────────

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_interface"))

    if request.method == "POST":
        entered_password = request.form.get("password", "")
        admin_password   = os.getenv("ADMIN_PASSWORD", "")

        if admin_password and hmac.compare_digest(entered_password, admin_password):
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("admin.admin_interface"))

        return render_template_string(LOGIN_TEMPLATE, error="Mot de passe incorrect."), 401

    return render_template_string(LOGIN_TEMPLATE)


@admin_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@admin_bp.route("/admin", methods=["GET"])
def admin_interface():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    return render_template_string(ADMIN_TEMPLATE)


@admin_bp.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    db_session = current_app.extensions["prospection_db_session"]
    Prospect   = current_app.extensions["prospection_prospect_model"]
    db         = db_session()

    try:
        prospects_count  = db.query(Prospect).count()
        new_count        = db.query(Prospect).filter(Prospect.status == "nouveau").count()
        contacted_count  = db.query(Prospect).filter(Prospect.status == "contacté").count()

        return jsonify({
            "prospects_count" : prospects_count,
            "new_count"       : new_count,
            "contacted_count" : contacted_count
        }), 200
    finally:
        db.close()


@admin_bp.route("/api/admin/chat", methods=["POST"])
def admin_chat():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    data        = request.get_json(silent=True) or {}
    instruction = (data.get("instruction") or "").strip()

    if not instruction:
        return jsonify({"error": "Instruction vide."}), 400

    db_session = current_app.extensions["prospection_db_session"]
    Prospect   = current_app.extensions["prospection_prospect_model"]
    db         = db_session()

    try:
        count = db.query(Prospect).count()

        answer = (
            f"Instruction reçue : {instruction}\\n\\n"
            f"Il y a actuellement {count} prospect(s) dans la base.\\n\\n"
            "L'interface fonctionne correctement. "
            "La prochaine étape sera de connecter ce chat aux actions réelles "
            "(ajouter des prospects, préparer des campagnes et générer des brouillons)."
        )

        return jsonify({"status": "success", "answer": answer}), 200
    finally:
        db.close()


def init_admin_interface(app, db_session, Prospect):
    flask_secret_key = os.getenv("FLASK_SECRET_KEY")

    if not flask_secret_key:
        raise RuntimeError(
            "FLASK_SECRET_KEY manquant. "
            "Ajoute cette variable dans Render > Environment."
        )

    if not os.getenv("ADMIN_PASSWORD"):
        raise RuntimeError(
            "ADMIN_PASSWORD manquant. "
            "Ajoute cette variable dans Render > Environment."
        )

    app.config["SECRET_KEY"] = flask_secret_key
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"]   = (
        os.getenv("ENV", "development").lower() == "production"
    )

    app.extensions["prospection_db_session"]      = db_session
    app.extensions["prospection_prospect_model"]  = Prospect

    if "admin" not in app.blueprints:
        app.register_blueprint(admin_bp)