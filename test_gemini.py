import os
import google.generativeai as genai

key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
print('Cle trouvee:', bool(key), '| len=', len(key or ''))
if not key:
    raise SystemExit('Pas de cle')

genai.configure(api_key=key)
models = [os.getenv('GEMINI_MODEL') or 'gemini-2.0-flash', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
last_err = None
for name in models:
    try:
        m = genai.GenerativeModel(name)
        r = m.generate_content('Reponds en une seule phrase courte: tu fonctionnes oui ou non?')
        print('OK modele:', name)
        print('Reponse :', (r.text or '').strip())
        break
    except Exception as e:
        last_err = e
        print('FAIL', name, '->', str(e)[:200])
else:
    print('AUCUN MODELE OK')
    raise SystemExit(last_err)
