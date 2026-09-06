import os, sys
key = (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or '').strip()
print('KEY ok:', bool(key), 'len:', len(key))
if not key:
    sys.exit('pas de cle')

import google.generativeai as genai
genai.configure(api_key=key)

print('\n=== MODELES LISTES PAR API ===')
usable = []
try:
    for m in genai.list_models():
        name = getattr(m, 'name', '')
        methods = list(getattr(m, 'supported_generation_methods', []) or [])
        if 'generateContent' in methods:
            short = name.replace('models/', '')
            usable.append(short)
            print('  OK generateContent:', short)
except Exception as e:
    print('list_models FAIL:', type(e).__name__, e)

print('\n=== TEST GENERATE ===')
# priorite moderne
priority = [
    'gemini-2.0-flash',
    'gemini-2.0-flash-001',
    'gemini-2.5-flash',
    'gemini-flash-latest',
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash-001',
    'gemini-1.5-pro',
    'gemini-1.5-pro-latest',
]
# ajouter ceux listes
for u in usable:
    if u not in priority:
        priority.append(u)

chosen = None
for name in priority:
    try:
        model = genai.GenerativeModel(name)
        r = model.generate_content('Reponds un seul mot: PONG')
        text = (getattr(r, 'text', None) or '').strip()
        if text:
            print('SUCCESS:', name, '->', text)
            chosen = name
            break
        else:
            print('EMPTY:', name)
    except Exception as e:
        print('FAIL:', name, '->', type(e).__name__, str(e)[:180])

if not chosen:
    print('\nAUCUN MODELE NE FONCTIONNE')
    sys.exit(2)

with open('working_model.txt', 'w', encoding='utf-8') as f:
    f.write(chosen)
print('\nCHOSEN=', chosen)
