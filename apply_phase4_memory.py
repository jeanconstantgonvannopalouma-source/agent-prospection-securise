import os, sys, ast, re
from pathlib import Path

main_path = Path("src/main.py")
code = main_path.read_text(encoding="utf-8-sig")

# 1. Modele DB KnowledgeBase
KB_MODEL = '''
class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    data_json = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
'''

if "class KnowledgeBase" not in code:
    code = code.replace("class Activity(Base):", KB_MODEL + "\nclass Activity(Base):")

# 2. Helpers et Tools KnowledgeBase
KB_HELPERS_TOOLS = '''
def get_kb_item(db, key):
    item = db.query(KnowledgeBase).filter(KnowledgeBase.key == key).first()
    if item and item.data_json:
        try:
            return json.loads(item.data_json)
        except Exception:
            return {}
    return {}

def set_kb_item(db, key, data_dict):
    item = db.query(KnowledgeBase).filter(KnowledgeBase.key == key).first()
    if not item:
        item = KnowledgeBase(key=key, data_json=json.dumps(data_dict, ensure_ascii=False))
        db.add(item)
    else:
        item.data_json = json.dumps(data_dict, ensure_ascii=False)
        item.updated_at = datetime.utcnow()
    db.commit()

def tool_save_offer_icp(db, offer_name="", offer_desc="", price="", target_icp="", pain_points="", objections=""):
    """Enregistre ou met a jour la fiche offre et ICP dans la memoire long terme."""
    current = get_kb_item(db, "active_offer")
    data = {
        "offer_name": offer_name or current.get("offer_name") or "Offre Principale",
        "offer_desc": offer_desc or current.get("offer_desc") or "",
        "price": price or current.get("price") or "",
        "target_icp": target_icp or current.get("target_icp") or "",
        "pain_points": pain_points or current.get("pain_points") or "",
        "objections": objections or current.get("objections") or "",
    }
    set_kb_item(db, "active_offer", data)
    try:
        log_activity(db, channel="system", action="save_memory", subject=f"Fiche Offre Mémorisée: {data['offer_name']}", status="done")
    except Exception:
        pass
    return {"ok": True, "message": "Fiche Offre et ICP mémorisées dans la base long terme !", "data": data}

def tool_get_offer_icp(db):
    """Recupere la fiche offre et ICP actuellement memorisee."""
    data = get_kb_item(db, "active_offer")
    return {"ok": True, "active_offer": data or "Aucune offre enregistrée pour le moment."}
'''

if "def tool_save_offer_icp" not in code:
    code = code.replace("def tool_generate_sequence", KB_HELPERS_TOOLS + "\n\ndef tool_generate_sequence")

# 3. Brancher dans execute_tool
EXEC_KB = '''if tool_name in ("save_offer_icp", "save_memory"):
        return tool_save_offer_icp(db, offer_name=args.get("offer_name"), offer_desc=args.get("offer_desc"), price=args.get("price"), target_icp=args.get("target_icp"), pain_points=args.get("pain_points"), objections=args.get("objections"))
    if tool_name in ("get_offer_icp", "get_memory"):
        return tool_get_offer_icp(db)
    '''

if "save_offer_icp" not in code[code.find("def execute_tool"):code.find("def execute_tool")+4000]:
    code = code.replace('if tool_name == "generate_sequence":', EXEC_KB + 'if tool_name == "generate_sequence":')

# 4. Injecter la Fiche Offre dans le contexte build_db_context
if "FICHE OFFRE EN MEMOIRE" not in code:
    old_db_ctx = 'return ('
    new_db_ctx = '''kb_offer = get_kb_item(db, "active_offer")
    kb_str = f"FICHE OFFRE EN MEMOIRE: Nom={kb_offer.get('offer_name','Non définie')} | Cible={kb_offer.get('target_icp','Non définie')} | Prix={kb_offer.get('price','-')} | Douleurs={kb_offer.get('pain_points','-')}" if kb_offer else "Aucune fiche offre mémorisée."
    return (
        f"{kb_str}\\n"'''
    code = code.replace("def build_db_context(db):\n    count =", "def build_db_context(db):\n    count =")
    code = code.replace('return (\n        f"Prospects:', new_db_ctx + '\n        f"Prospects:')

# 5. Routes API KnowledgeBase
API_KB = '''
@app.route("/api/kb/offer", methods=["GET", "POST"])
def kb_offer_route():
    db = SessionLocal()
    try:
        if request.method == "POST":
            data = request.get_json() or {}
            res = tool_save_offer_icp(db, **data)
            return jsonify(res), 200
        return jsonify(tool_get_offer_icp(db)), 200
    finally:
        db.close()
'''

if "/api/kb/offer" not in code:
    code = code.replace('@app.route("/ui")', API_KB + '\n@app.route("/ui")')

# 6. Mettre a jour l'UI avec l'Onglet 4 (Memoire & Offres)
if "tab-memory" not in code:
    # Ajouter le bouton d'onglet
    code = code.replace(
        '<button class="tab-btn" onclick="switchTab(\'sequences\')">📜 Studio Séquences & Templates</button>',
        '<button class="tab-btn" onclick="switchTab(\'sequences\')">📜 Studio Séquences & Templates</button>\n        <button class="tab-btn" onclick="switchTab(\'memory\')">🧠 Mémoire & Offres</button>'
    )
    
    # Ajouter le contenu de l'onglet Mémoire
    MEMORY_TAB_HTML = '''
        <!-- TAB 4: KNOWLEDGE BASE MEMORY -->
        <div id="tab-memory" class="tab-content">
            <div class="card" style="padding: 24px; max-width: 800px; margin: 0 auto;">
                <h3 style="margin-bottom: 8px;">🧠 Mémoire Long Terme & Fiche Offre / ICP</h3>
                <p style="font-size: 13px; color: #94a3b8; margin-bottom: 20px;">L'agent utilise automatiquement ces informations pour personnaliser toutes ses réponses, emails et séquences sans que tu n'aies à lui répéter.</p>

                <div class="modal-form">
                    <label style="font-size:12px; color:#38bdf8; font-weight:600;">Nom de l'Offre / Service</label>
                    <input id="kb-name" placeholder="Ex: Création de site web Premium pour Agences Immo">

                    <label style="font-size:12px; color:#38bdf8; font-weight:600;">Description de l'Offre & Promesse</label>
                    <textarea id="kb-desc" rows="3" placeholder="Ex: Nous concevons des sites web modernes avec estimation en ligne qui multiplient les mandats exclusifs."></textarea>

                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                        <div>
                            <label style="font-size:12px; color:#38bdf8; font-weight:600;">Tarif / Pricing</label>
                            <input id="kb-price" placeholder="Ex: 1 500 € ou 150 €/mois">
                        </div>
                        <div>
                            <label style="font-size:12px; color:#38bdf8; font-weight:600;">Cible Idéale (ICP)</label>
                            <input id="kb-target" placeholder="Ex: Directeurs d'agences immobilières indépendantes">
                        </div>
                    </div>

                    <label style="font-size:12px; color:#38bdf8; font-weight:600;">Principales Douleurs Résolues</label>
                    <input id="kb-pains" placeholder="Ex: Manque de visibilité web, sites obsolètes, perte de mandats face aux réseaux">

                    <label style="font-size:12px; color:#38bdf8; font-weight:600;">Objections courantes & Réponses</label>
                    <input id="kb-objs" placeholder="Ex: 'C'est trop cher' -> Rentabilisé dès le premier mandat signé.">

                    <button class="btn btn-primary" style="margin-top:10px;" onclick="saveMemoryUI()">💾 Mémoriser dans l'IA</button>
                </div>
            </div>
        </div>
    '''
    code = code.replace('<div id="tab-sequences" class="tab-content">', MEMORY_TAB_HTML + '\n        <div id="tab-sequences" class="tab-content">')

    # Ajouter le JS pour charger et sauvegarder la mémoire
    MEMORY_JS = '''
        async function loadMemoryUI() {
            try {
                const r = await fetch('/api/kb/offer');
                const d = await r.json();
                const o = d.active_offer || {};
                document.getElementById('kb-name').value = o.offer_name || '';
                document.getElementById('kb-desc').value = o.offer_desc || '';
                document.getElementById('kb-price').value = o.price || '';
                document.getElementById('kb-target').value = o.target_icp || '';
                document.getElementById('kb-pains').value = o.pain_points || '';
                document.getElementById('kb-objs').value = o.objections || '';
            } catch(e){}
        }

        async function saveMemoryUI() {
            const body = {
                offer_name: document.getElementById('kb-name').value,
                offer_desc: document.getElementById('kb-desc').value,
                price: document.getElementById('kb-price').value,
                target_icp: document.getElementById('kb-target').value,
                pain_points: document.getElementById('kb-pains').value,
                objections: document.getElementById('kb-objs').value,
            };
            const r = await fetch('/api/kb/offer', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
            const d = await r.json();
            alert(d.message || 'Mémorisé !');
        }
    '''
    code = code.replace("addMsg('agent', 'Bonjour Jean Constant ! Ton Dashboard Prospection Phase 3", MEMORY_JS + "\n        loadMemoryUI();\n        addMsg('agent', 'Bonjour Jean Constant ! Ton Dashboard Prospection avec Mémoire Long Terme est actif.")

main_path.write_text(code, encoding="utf-8")

b = main_path.read_bytes()
if b.startswith(b"\xef\xbb\xbf"):
    main_path.write_bytes(b[3:])

ast.parse(main_path.read_text(encoding="utf-8"))
print("--> PHASE 4 (MEMOIRE LONG TERME & FICHE OFFRE) APPLIQUEE AVEC SUCCES !")