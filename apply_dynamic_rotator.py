import os, sys, ast, re
from pathlib import Path

main_path = Path("src/main.py")
code = main_path.read_text(encoding="utf-8-sig")

# 1. Nouveau Rotator Dynamique et Silencieux
DYNAMIC_ROTATOR = '''
# ===================== DYNAMIC SILENT GEMINI ROTATOR =====================
def call_gemini_with_rotation(prompt_text):
    """Bascule automatiquement et silencieusement entre les modeles Gemini valides."""
    global ACTIVE_MODEL_NAME, GEMINI_AVAILABLE, LAST_GEMINI_ERROR, genai
    key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip().strip('"').strip("'")
    if not key:
        return None, None, "Clé GEMINI_API_KEY manquante dans le fichier .env"
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
    except Exception as e:
        return None, None, f"Erreur de configuration Google API: {e}"

    # 1. Obtenir les modeles reels supportes par l'API
    discovered_models = []
    try:
        for m in genai.list_models():
            methods = list(getattr(m, "supported_generation_methods", []) or [])
            if "generateContent" in methods:
                name = getattr(m, "name", "").replace("models/", "")
                if name and "gemini" in name.lower() and not any(b in name.lower() for b in ["gemma", "3.8", "chat-bison", "1.0-pro"]):
                    discovered_models.append(name)
    except Exception as e:
        logger.warning(f"list_models dynamique echoue, utilisation de la liste de secours: {e}")

    # Modeles de secours si la liste dynamique echoue
    fallback_list = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash-001",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash-001"
    ]
    
    # Combiner et ordonner
    pref = (os.getenv("GEMINI_MODEL") or "gemini-2.0-flash").strip()
    cands = [pref] if pref else []
    for m_name in discovered_models + fallback_list:
        if m_name and m_name not in cands and not any(b in m_name.lower() for b in ["gemma", "3.8", "chat-bison"]):
            cands.append(m_name)

    # 2. Tester les modeles un par un silencieusement
    for model_name in cands:
        try:
            m = genai.GenerativeModel(model_name)
            res = m.generate_content(
                prompt_text,
                generation_config={
                    "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.3") or 0.3),
                    "max_output_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "2048") or 2048),
                }
            )
            txt = (getattr(res, "text", None) or "").strip()
            if txt:
                ACTIVE_MODEL_NAME = model_name
                GEMINI_AVAILABLE = True
                LAST_GEMINI_ERROR = None
                return txt, model_name, None
        except Exception as e:
            # On ignore silencieusement les 404, 429 et 500 et on passe au modele suivant
            logger.info(f"Bascule modele: {model_name} non disponible ({type(e).__name__}) -> Recherche du suivant...")
            continue

    return None, None, "Les modèles Gemini gratuits sont temporairement en pause de quota. Réessaie dans 30 secondes !"
# =========================================================================
'''

# Inserer le Rotator Dynamique
if "def call_gemini_with_rotation" in code:
    code = re.sub(
        r"# ===================== GEMINI ROTATOR =====================[\s\S]*?# ==========================================================",
        DYNAMIC_ROTATOR.strip(),
        code
    )
else:
    if "def ask_agent" in code:
        code = code.replace("def ask_agent", DYNAMIC_ROTATOR + "\n\ndef ask_agent", 1)

# Nettoyer l'affichage de l'erreur dans la route chat pour avoir un message propre
old_chat_err = 'return f"Erreur Gemini: {err_res}", meta'
new_chat_err = 'return err_res, meta'

if old_chat_err in code:
    code = code.replace(old_chat_err, new_chat_err)

main_path.write_text(code, encoding="utf-8")

b = main_path.read_bytes()
if b.startswith(b"\xef\xbb\xbf"):
    main_path.write_bytes(b[3:])

ast.parse(main_path.read_text(encoding="utf-8"))
print("--> ROTATOR DYNAMIQUE ET SILENCIEUX APPLIQUE AVEC SUCCES !")