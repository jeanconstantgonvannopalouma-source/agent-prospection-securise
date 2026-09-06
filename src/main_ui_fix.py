import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/ui")
def ui():
    try:
        # Chemin ABSOLU qui marche à 100% sur Render
        template_path = os.path.join(os.path.dirname(__file__), "templates", "ui.html")
        return render_template(template_path)
    except Exception as e:
        return f"Erreur template: {str(e)}", 500
