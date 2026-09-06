from pathlib import Path
path = Path('src/main.py')
text = path.read_text(encoding='utf-8')

old_boot = '''
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        candidates = [GEMINI_MODEL_ENV, "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        # de-dup
        seen = set()
        models_to_try = []
        for n in candidates:
            if n and n not in seen:
                seen.add(n)
                models_to_try.append(n)
        for name in models_to_try:
            try:
                m = genai.GenerativeModel(name)
                # vrai smoke test
                r = m.generate_content("Reponds un mot: OK")
                txt = (getattr(r, "text", None) or "").strip()
                if txt:
                    ACTIVE_MODEL_NAME = name
                    GEMINI_AVAILABLE = True
                    logger.info(f"Gemini OK smoke-test: {name} -> {txt[:40]}")
                    break
                else:
                    logger.warning(f"Modele {name} reponse vide au smoke-test")
            except Exception as e:
                LAST_GEMINI_ERROR = f"{type(e).__name__}: {e}"
                logger.warning(f"Modele {name} fail: {LAST_GEMINI_ERROR}")
        if not GEMINI_AVAILABLE:
            logger.error(f"Aucun modele Gemini utilisable. Derniere erreur: {LAST_GEMINI_ERROR}")
    else:
        LAST_GEMINI_ERROR = "GEMINI_API_KEY manquante"
        logger.warning(LAST_GEMINI_ERROR)
except Exception as e:
    LAST_GEMINI_ERROR = f"Import/config: {type(e).__name__}: {e}"
    logger.error(LAST_GEMINI_ERROR)
'''

new_boot = '''
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        candidates = []
        # 1) modele force via env
        if GEMINI_MODEL_ENV:
            candidates.append(GEMINI_MODEL_ENV)
        # 2) modeles modernes (plus de gemini-pro legacy)
        candidates += [
            "gemini-2.0-flash",
            "gemini-2.0-flash-001",
            "gemini-2.5-flash",
            "gemini-flash-latest",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash-001",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
        ]
        # 3) modeles dynamiques exposes par l API
        try:
            for m in genai.list_models():
                methods = list(getattr(m, "supported_generation_methods", []) or [])
                if "generateContent" in methods:
                    short = (getattr(m, "name", "") or "").replace("models/", "")
                    if short:
                        candidates.append(short)
        except Exception as e:
            logger.warning(f"list_models impossible: {e}")

        seen = set()
        models_to_try = []
        for n in candidates:
            n = (n or "").strip()
            if not n or n in seen:
                continue
            # ignorer explicitement les modeles morts
            if n in {"gemini-pro", "gemini-1.0-pro", "chat-bison-001"}:
                continue
            seen.add(n)
            models_to_try.append(n)

        for name in models_to_try:
            try:
                m = genai.GenerativeModel(name)
                r = m.generate_content("Reponds un mot: OK")
                txt = (getattr(r, "text", None) or "").strip()
                if txt:
                    ACTIVE_MODEL_NAME = name
                    GEMINI_AVAILABLE = True
                    LAST_GEMINI_ERROR = None
                    logger.info(f"Gemini OK smoke-test: {name} -> {txt[:40]}")
                    break
                else:
                    logger.warning(f"Modele {name} reponse vide au smoke-test")
            except Exception as e:
                LAST_GEMINI_ERROR = f"{type(e).__name__}: {e}"
                logger.warning(f"Modele {name} fail: {LAST_GEMINI_ERROR}")
        if not GEMINI_AVAILABLE:
            logger.error(f"Aucun modele Gemini utilisable. Derniere erreur: {LAST_GEMINI_ERROR}")
    else:
        LAST_GEMINI_ERROR = "GEMINI_API_KEY manquante"
        logger.warning(LAST_GEMINI_ERROR)
except Exception as e:
    LAST_GEMINI_ERROR = f"Import/config: {type(e).__name__}: {e}"
    logger.error(LAST_GEMINI_ERROR)
'''

# fallback si exact match fail: on reecrit le fichier boot autrement via marqueurs
if old_boot.strip() in text:
    text = text.replace(old_boot.strip(), new_boot.strip())
else:
    # tentative soft: remplacer la liste candidates hardcodee
    text = text.replace(
        'candidates = [GEMINI_MODEL_ENV, "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]',
        'candidates = [GEMINI_MODEL_ENV, "gemini-2.0-flash", "gemini-2.0-flash-001", "gemini-2.5-flash", "gemini-flash-latest", "gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro"]'
    )
    text = text.replace('"gemini-pro"', '"gemini-1.5-flash"')
    text = text.replace("'gemini-pro'", "'gemini-1.5-flash'")

path.write_text(text, encoding='utf-8')
print('main.py model boot patched')
print('GEMINI_MODEL forced to', open('working_model.txt', encoding='utf-8').read().strip())
