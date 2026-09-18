from pathlib import Path
import ast, re

main_path = Path("src/main.py")
code = main_path.read_text(encoding="utf-8-sig")

# Nouvelle UI HTML/JS Complète Phase 3
DASHBOARD_UI_CODE = r'''
@app.route("/ui")
def ui():
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent de Prospection — Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; min-height: 100vh; }
        .app-header { background: #1e293b; border-bottom: 1px solid #334155; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }
        .logo h1 { font-size: 20px; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px; }
        .logo p { font-size: 12px; color: #94a3b8; }
        .controls { display: flex; align-items: center; gap: 10px; }
        .badge { font-size: 12px; padding: 4px 10px; border-radius: 999px; background: #334155; color: #cbd5e1; font-weight: 600; }
        .btn { border: None; border-radius: 8px; padding: 8px 14px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
        .btn-primary { background: #0284c7; color: white; } .btn-primary:hover { background: #0369a1; }
        .btn-dry { background: #fef08a; color: #854d0e; } .btn-live { background: #fecaca; color: #991b1b; }
        .btn-dark { background: #334155; color: white; } .btn-dark:hover { background: #475569; }
        .btn-danger { background: #ef4444; color: white; } .btn-danger:hover { background: #dc2626; }
        .btn-sm { padding: 4px 8px; font-size: 11px; border-radius: 6px; }

        /* TAB NAVIGATION */
        .tabs { display: flex; background: #1e293b; border-bottom: 1px solid #334155; padding: 0 24px; gap: 4px; }
        .tab-btn { background: transparent; border: none; color: #94a3b8; padding: 12px 20px; font-size: 14px; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s; }
        .tab-btn:hover { color: #f1f5f9; }
        .tab-btn.active { color: #38bdf8; border-bottom-color: #38bdf8; }

        .container { max-width: 1400px; margin: 0 auto; padding: 24px; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* STATS GRID */
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px; text-align: center; }
        .stat-val { font-size: 26px; font-weight: 700; color: #38bdf8; }
        .stat-lbl { font-size: 12px; color: #94a3b8; margin-top: 4px; }

        /* CHAT VIEW GRID */
        .chat-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        @media (max-width: 900px) { .chat-layout { grid-template-columns: 1fr; } .stats-grid { grid-template-columns: repeat(2, 1fr); } }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; }
        .card-header { padding: 16px 20px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
        .card-header h3 { font-size: 15px; color: #f8fafc; }
        .chips { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
        .chip { background: #334155; color: #e2e8f0; border: none; border-radius: 999px; padding: 4px 10px; font-size: 11px; cursor: pointer; }
        .chip:hover { background: #475569; }

        #messages { height: 420px; overflow-y: auto; padding: 20px; background: #0f172a; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 85%; padding: 12px 16px; border-radius: 12px; font-size: 14px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; }
        .msg-user { margin-left: auto; background: #0284c7; color: white; border-bottom-right-radius: 2px; }
        .msg-agent { margin-right: auto; background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-bottom-left-radius: 2px; }
        .msg-meta { font-size: 10px; color: #64748b; margin-top: 4px; }

        .chat-input-bar { display: flex; gap: 10px; padding: 14px; background: #1e293b; border-top: 1px solid #334155; }
        .chat-input-bar input { flex: 1; background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 10px 14px; color: white; font-size: 14px; outline: none; }
        .chat-input-bar input:focus { border-color: #38bdf8; }

        /* PROSPECTS TABLE VIEW */
        .table-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; gap: 12px; flex-wrap: wrap; }
        .search-box { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 8px 14px; color: white; font-size: 13px; width: 280px; }
        .filter-select { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 8px 12px; color: white; font-size: 13px; }
        .prospects-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
        .prospects-table th { background: #1e293b; padding: 12px 16px; color: #94a3b8; font-weight: 600; border-bottom: 1px solid #334155; }
        .prospects-table td { padding: 12px 16px; border-bottom: 1px solid #334155; color: #e2e8f0; }
        .prospects-table tr:hover td { background: #1e293b; }
        .status-badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }
        .st-nouveau { background: #0284c7; color: white; }
        .st-contacte { background: #eab308; color: black; }
        .st-en_sequence { background: #a855f7; color: white; }

        /* MODAL */
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); align-items: center; justify-content: center; z-index: 100; }
        .modal.active { display: flex; }
        .modal-content { background: #1e293b; border: 1px solid #334155; border-radius: 14px; width: 500px; max-width: 90%; padding: 24px; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .modal-form { display: grid; gap: 12px; }
        .modal-form input, .modal-form select, .modal-form textarea { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 10px; color: white; font-size: 13px; }

        /* ACTIVITIES TIMELINE */
        .act-list { height: 420px; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
        .act-item { background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 12px; font-size: 12px; }
        .act-top { display: flex; justify-content: space-between; margin-bottom: 4px; font-weight: 600; }
    </style>
</head>
<body>
    <div class="app-header">
        <div class="logo">
            <h1>🚀 Agent Prospection</h1>
            <p>Copilote Commercial & Automatisations</p>
        </div>
        <div class="controls">
            <span class="badge" id="ai-status">IA: ...</span>
            <span class="badge" id="mail-status">Email: ...</span>
            <button class="btn btn-dry" id="btn-dry" onclick="setMode(true)">Mode DRY_RUN</button>
            <button class="btn btn-live" id="btn-live" onclick="confirmLive()">Mode LIVE</button>
        </div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('chat')">💬 Copilote Chat</button>
        <button class="tab-btn" onclick="switchTab('prospects')">👥 Gestionnaire Prospects</button>
        <button class="tab-btn" onclick="switchTab('sequences')">📜 Studio Séquences & Templates</button>
    </div>

    <div class="container">
        <!-- GLOBAL STATS -->
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-val" id="count-total">0</div><div class="stat-lbl">Prospects Total</div></div>
            <div class="stat-card"><div class="stat-val" id="count-new">0</div><div class="stat-lbl">Nouveaux</div></div>
            <div class="stat-card"><div class="stat-val" id="count-contacted">0</div><div class="stat-lbl">Contactés / En séquence</div></div>
            <div class="stat-card"><div class="stat-val" id="count-mails">0</div><div class="stat-lbl">Emails Aujourd'hui (Quota)</div></div>
        </div>

        <!-- TAB 1: CHAT -->
        <div id="tab-chat" class="tab-content active">
            <div class="chat-layout">
                <div class="card">
                    <div class="card-header">
                        <h3>Assistant IA Prospection</h3>
                        <div class="chips">
                            <button class="chip" onclick="sendMsg('Lister mes prospects')">Lister prospects</button>
                            <button class="chip" onclick="sendMsg('Génère une séquence de prospection 3 emails + 2 LinkedIn pour des agences immo')">Séquence Immo</button>
                            <button class="chip" onclick="sendMsg('Préparer un email de relance en simulation pour jcgp471@gmail.com')">Email Relance</button>
                        </div>
                    </div>
                    <div id="messages"></div>
                    <form class="chat-input-bar" id="chat-form">
                        <input id="prompt" placeholder="Demande une action à ton agent..." autocomplete="off" required>
                        <button class="btn btn-primary" type="submit">Envoyer</button>
                    </form>
                </div>

                <div class="card">
                    <div class="card-header"><h3>Activités Récentes</h3></div>
                    <div class="act-list" id="activities"></div>
                </div>
            </div>
        </div>

        <!-- TAB 2: PROSPECTS CRM -->
        <div id="tab-prospects" class="tab-content">
            <div class="table-toolbar">
                <div style="display:flex; gap:10px;">
                    <input class="search-box" id="search-input" placeholder="🔍 Rechercher un prospect..." oninput="filterProspects()">
                    <select class="filter-select" id="status-filter" onchange="filterProspects()">
                        <option value="">Tous les statuts</option>
                        <option value="nouveau">Nouveau</option>
                        <option value="contacté">Contacté</option>
                        <option value="en_sequence">En Séquence</option>
                    </select>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-dark" onclick="openAddModal()">➕ Ajouter un prospect</button>
                    <button class="btn btn-primary" onclick="document.getElementById('csv-file').click()">📥 Importer CSV</button>
                    <input type="file" id="csv-file" accept=".csv" style="display:none" onchange="uploadCSV(this)">
                </div>
            </div>

            <div class="card">
                <table class="prospects-table">
                    <thead>
                        <tr>
                            <th>Nom & Prénom</th>
                            <th>Email</th>
                            <th>Entreprise & Poste</th>
                            <th>Statut</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="prospects-tbody"></tbody>
                </table>
            </div>
        </div>

        <!-- TAB 3: SEQUENCES & TEMPLATES -->
        <div id="tab-sequences" class="tab-content">
            <div class="card" style="padding: 24px; margin-bottom:20px;">
                <h3 style="margin-bottom:12px;">⚡ Studio de Génération de Séquences</h3>
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr auto; gap:10px;">
                    <input class="search-box" id="seq-offer" placeholder="Offre (ex: Création site web)" style="width:100%">
                    <input class="search-box" id="seq-target" placeholder="Cible (ex: Agences Immobilières)" style="width:100%">
                    <select class="filter-select" id="seq-channel">
                        <option value="both">Email + LinkedIn</option>
                        <option value="email">Email uniquement</option>
                        <option value="linkedin">LinkedIn uniquement</option>
                    </select>
                    <button class="btn btn-primary" onclick="generateStudioSeq()">Générer la séquence</button>
                </div>
            </div>

            <div id="templates-preview" class="card" style="padding: 24px;">
                <h3>Modèles d'Emails & Messages LinkedIn</h3>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:16px;">
                    <div style="background:#0f172a; padding:16px; border-radius:10px; border:1px solid #334155;">
                        <h4 style="color:#38bdf8;">📧 Prise de contact Email</h4>
                        <p style="font-size:12px; color:#94a3b8; margin-top:8px;">Objet: {first_name}, une idée rapide pour {company}</p>
                        <p style="font-size:12px; color:#cbd5e1; margin-top:8px;">Bonjour {first_name},<br><br>En regardant {company}, j'ai pensé à une piste simple pour {job_title}...<br><br>Seriez-vous ouvert à 15 min d'échange ?</p>
                    </div>
                    <div style="background:#0f172a; padding:16px; border-radius:10px; border:1px solid #334155;">
                        <h4 style="color:#a855f7;">💼 LinkedIn Invitation</h4>
                        <p style="font-size:12px; color:#cbd5e1; margin-top:8px;">Bonjour {first_name}, j'accompagne des profils comme {job_title} chez {company}. OK pour se connecter ?</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL AJOUT PROSPECT -->
    <div class="modal" id="add-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Nouveau Prospect</h3>
                <button class="btn btn-sm btn-dark" onclick="closeAddModal()">✕</button>
            </div>
            <div class="modal-form">
                <input id="m-first" placeholder="Prénom">
                <input id="m-last" placeholder="Nom">
                <input id="m-email" placeholder="Email *">
                <input id="m-company" placeholder="Entreprise">
                <input id="m-job" placeholder="Poste">
                <button class="btn btn-primary" onclick="submitAddModal()">Enregistrer</button>
            </div>
        </div>
    </div>

    <script>
        const sessionId = localStorage.getItem('ps_session') || (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()));
        localStorage.setItem('ps_session', sessionId);
        let allProspects = [];

        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + tab).classList.add('active');
            if (tab === 'prospects') loadProspects();
        }

        function addMsg(role, text, meta) {
            const messages = document.getElementById('messages');
            const d = document.createElement('div');
            d.className = 'msg ' + (role === 'user' ? 'msg-user' : 'msg-agent');
            d.textContent = text;
            if (meta) {
                const m = document.createElement('div');
                m.className = 'msg-meta';
                m.textContent = meta;
                d.appendChild(m);
            }
            messages.appendChild(d);
            messages.scrollTop = messages.scrollHeight;
        }

        async function loadStats() {
            try {
                const d = await (await fetch('/api/admin/stats')).json();
                document.getElementById('count-total').textContent = d.prospects_count || 0;
                document.getElementById('count-new').textContent = d.new_count || 0;
                document.getElementById('count-contacted').textContent = d.contacted_count || 0;
                const es = d.email_stats || {};
                document.getElementById('count-mails').textContent = (es.sent_or_simulated_today || 0) + '/' + (es.max_per_day || 30);
            } catch(e) {}
        }

        async function loadHealth() {
            try {
                const d = await (await fetch('/health')).json();
                const ai = document.getElementById('ai-status');
                const mail = document.getElementById('mail-status');
                ai.textContent = d.gemini === 'ok' ? ('IA: ON (' + (d.model || '') + ')') : 'IA: FALLBACK';
                mail.textContent = d.email_mode === 'DRY_RUN' ? 'Email: DRY_RUN (Simulation)' : 'Email: LIVE (Envois Réels)';
                mail.style.background = d.email_mode === 'DRY_RUN' ? '#fef08a' : '#fecaca';
                mail.style.color = d.email_mode === 'DRY_RUN' ? '#854d0e' : '#991b1b';
            } catch(e) {}
        }

        async function loadActivities() {
            try {
                const d = await (await fetch('/api/activities?limit=25')).json();
                const box = document.getElementById('activities');
                box.innerHTML = '';
                (d.activities || []).forEach(a => {
                    const el = document.createElement('div');
                    el.className = 'act-item';
                    el.innerHTML = `<div class="act-top"><span>${a.action}</span><span style="color:${a.status==='sent'?'#4ade80':'#facc15'}">${a.status}</span></div><div>${a.email_to || '-'}</div><div style="color:#94a3b8; font-size:11px;">${a.subject || ''}</div>`;
                    box.appendChild(el);
                });
            } catch(e) {}
        }

        async function loadProspects() {
            try {
                const d = await (await fetch('/api/prospects?limit=100')).json();
                allProspects = d.prospects || [];
                renderProspectsTable(allProspects);
            } catch(e) {}
        }

        function renderProspectsTable(list) {
            const tbody = document.getElementById('prospects-tbody');
            tbody.innerHTML = '';
            list.forEach(p => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${p.first_name || ''} ${p.last_name || ''}</strong></td>
                    <td>${p.email}</td>
                    <td>${p.company || 'N/A'} <span style="color:#94a3b8">(${p.job_title || 'N/A'})</span></td>
                    <td><span class="status-badge st-${p.status || 'nouveau'}">${p.status || 'nouveau'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-dark" onclick="sendMsg('Email DRY_RUN pour ${p.email}')">📧 Mail</button>
                        <button class="btn btn-sm btn-dark" onclick="sendMsg('Génère LinkedIn pour ${p.email}')">💼 LinkedIn</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteProspect('${p.email}')">🗑️</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function filterProspects() {
            const query = document.getElementById('search-input').value.toLowerCase();
            const status = document.getElementById('status-filter').value;
            const filtered = allProspects.filter(p => {
                const matchQuery = (p.first_name + ' ' + p.last_name + ' ' + p.email + ' ' + p.company).toLowerCase().includes(query);
                const matchStatus = !status || p.status === status;
                return matchQuery && matchStatus;
            });
            renderProspectsTable(filtered);
        }

        async function sendMsg(msg) {
            switchTab('chat');
            addMsg('user', msg);
            try {
                const r = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: msg, session_id: sessionId }) });
                const d = await r.json();
                addMsg('agent', d.reply || d.error || 'Erreur', 'engine=' + (d.engine || '?'));
                loadStats(); loadHealth(); loadActivities(); loadProspects();
            } catch(e) { addMsg('agent', 'Erreur de connexion'); }
        }

        document.getElementById('chat-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const input = document.getElementById('prompt');
            const msg = input.value.trim();
            if (!msg) return;
            input.value = '';
            sendMsg(msg);
        });

        async function setMode(dry) {
            const r = await fetch('/api/config/email-mode', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ dry_run: dry }) });
            const d = await r.json();
            loadHealth();
        }

        function confirmLive() {
            if (confirm('Activer le mode LIVE ? Les emails partent VRAIMENT.')) setMode(false);
        }

        function openAddModal() { document.getElementById('add-modal').classList.add('active'); }
        function closeAddModal() { document.getElementById('add-modal').classList.remove('active'); }

        async function submitAddModal() {
            const body = {
                first_name: document.getElementById('m-first').value,
                last_name: document.getElementById('m-last').value,
                email: document.getElementById('m-email').value,
                company: document.getElementById('m-company').value,
                job_title: document.getElementById('m-job').value,
            };
            if (!body.email) return alert('Email requis');
            await fetch('/api/prospects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
            closeAddModal();
            loadProspects(); loadStats();
        }

        async function deleteProspect(email) {
            if (confirm('Supprimer définitivement le prospect ' + email + ' ?')) {
                sendMsg('Supprime le prospect ' + email);
            }
        }

        async function uploadCSV(input) {
            if (!input.files[0]) return;
            const fd = new FormData();
            fd.append('file', input.files[0]);
            const r = await fetch('/api/prospects/import', { method: 'POST', body: fd });
            const d = await r.json();
            alert(d.ok ? (d.imported + ' prospects importés !') : 'Erreur: ' + d.error);
            input.value = '';
            loadProspects(); loadStats();
        }

        function generateStudioSeq() {
            const offer = document.getElementById('seq-offer').value;
            const target = document.getElementById('seq-target').value;
            const channel = document.getElementById('seq-channel').value;
            if (!offer || !target) return alert('Précise l\'offre et la cible');
            sendMsg(`Génère une séquence de prospection pour vendre ${offer} à ${target} (Canal: ${channel})`);
        }

        addMsg('agent', 'Bonjour Jean Constant ! Ton Dashboard Prospection Phase 3 est actif. Navigue entre le Chat, tes Prospects et tes Séquences.');
        loadStats(); loadHealth(); loadActivities(); loadProspects();
    </script>
</body>
</html>"""
    return Response(html, mimetype="text/html")
'''

# Remplacer la fonction ui() existante par la nouvelle
if '@app.route("/ui")' in code:
    code = re.sub(
        r'@app\.route\("/ui"\)[\s\S]*?def ui\(\):[\s\S]*?return Response\(html, mimetype="text/html"\)',
        DASHBOARD_UI_CODE.strip(),
        code
    )

main_path.write_text(code, encoding="utf-8")

b = main_path.read_bytes()
if b.startswith(b"\xef\xbb\xbf"):
    main_path.write_bytes(b[3:])

ast.parse(main_path.read_text(encoding="utf-8"))
print("--> DASHBOARD UI PHASE 3 APPLIQUE AVEC SUCCES !")