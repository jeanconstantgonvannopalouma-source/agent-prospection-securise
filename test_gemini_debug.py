import os, traceback
key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
print('KEY', bool(key), len(key or ''), (key or '')[:6], '...', (key or '')[-4:])
import google.generativeai as genai
genai.configure(api_key=key)
for name in [os.getenv('GEMINI_MODEL') or 'gemini-2.0-flash','gemini-2.0-flash','gemini-1.5-flash','gemini-1.5-pro','gemini-pro','models/gemini-1.5-flash']:
    try:
        m = genai.GenerativeModel(name)
        r = m.generate_content('Dis seulement: PONG')
        print('SUCCESS', name, '->', repr(getattr(r,'text',None)))
        break
    except Exception as e:
        print('FAIL', name, '->', type(e).__name__, str(e)[:300])
        traceback.print_exc()
        print('---')
