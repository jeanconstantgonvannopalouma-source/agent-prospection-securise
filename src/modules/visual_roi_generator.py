"""
GÉNÉRATEUR DE DASHBOARD VISUEL INTERACTIF HTML / SVG SUR-MESURE (VISUAL PROOF ENGINE)
"""
import os
import time

class VisualROIGenerator:
    """Génère une page web interactive personnalisée de démonstration de ROI pour le prospect"""

    def generate_html_roi_report(self, company_name: str, prospect_name: str, current_leads: int = 20, projected_leads: int = 65, avg_deal_val: float = 3500.0) -> str:
        os.makedirs("data/reports", exist_ok=True)
        filename = f"data/reports/roi_audit_{company_name.lower().replace(' ', '_')}.html"

        revenue_current = current_leads * avg_deal_val * 0.20
        revenue_projected = projected_leads * avg_deal_val * 0.25
        gain_annuel = (revenue_projected - revenue_current) * 12

        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Simulation Stratégique de Croissance - {company_name}</title>
    <style>
        body {{
            background-color: #0b0f19;
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 40px;
        }}
        .container {{
            max-width: 900px;
            margin: auto;
            background: #131b2e;
            padding: 35px;
            border-radius: 16px;
            border: 1px solid #23304d;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
        }}
        .header {{
            border-bottom: 1px solid #23304d;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{ color: #38bdf8; margin: 0 0 10px 0; font-size: 26px; }}
        .badge {{
            background: #0369a1;
            color: #bae6fd;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 35px;
        }}
        .metric-card {{
            background: #1a243b;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #2d3d63;
            text-align: center;
        }}
        .metric-val {{
            font-size: 28px;
            font-weight: 700;
            color: #10b981;
            margin-top: 8px;
        }}
        .chart-box {{
            background: #1a243b;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #2d3d63;
            margin-bottom: 30px;
        }}
        .footer-cta {{
            text-align: center;
            padding-top: 20px;
        }}
        .btn {{
            background: #2563eb;
            color: white;
            padding: 14px 28px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            display: inline-block;
            transition: 0.2s;
        }}
        .btn:hover {{ background: #1d4ed8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="badge">AUDIT STRATÉGIQUE EXCLUSIF</span>
            <h1>Plan de Croissance Commerciale par IA : {company_name}</h1>
            <p style="color: #94a3b8; margin: 0;">Préparé spécialement pour <strong>{prospect_name}</strong> • Modèle Prédictif V12.0</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div style="color: #94a3b8; font-size: 13px;">RDVs Mensuels Projetés</div>
                <div class="metric-val">{projected_leads} / mois</div>
            </div>
            <div class="metric-card">
                <div style="color: #94a3b8; font-size: 13px;">Accélération Pipeline</div>
                <div class="metric-val">+{int(((projected_leads - current_leads)/current_leads)*100)}%</div>
            </div>
            <div class="metric-card">
                <div style="color: #94a3b8; font-size: 13px;">Gain Annuel Estimé</div>
                <div class="metric-val">+{gain_annuel:,.0f} €</div>
            </div>
        </div>

        <div class="chart-box">
            <h3 style="margin-top: 0; color: #f8fafc;">📈 Comparatif de Génération de Pipeline B2B (€)</h3>
            <svg viewBox="0 0 700 180" style="width: 100%; height: auto;">
                <!-- Bar 1: Actuel -->
                <rect x="100" y="80" width="160" height="70" rx="8" fill="#475569" />
                <text x="180" y="65" fill="#94a3b8" text-anchor="middle" font-size="14" font-weight="bold">Actuel (~{revenue_current:,.0f} €/m)</text>
                
                <!-- Bar 2: Avec IA -->
                <rect x="400" y="20" width="160" height="130" rx="8" fill="#10b981" />
                <text x="480" y="12" fill="#10b981" text-anchor="middle" font-size="14" font-weight="bold">Avec Agent IA (~{revenue_projected:,.0f} €/m)</text>

                <!-- Axe -->
                <line x1="50" y1="150" x2="650" y2="150" stroke="#334155" stroke-width="2" />
            </svg>
        </div>

        <div class="footer-cta">
            <p style="color: #cbd5e1; margin-bottom: 20px;">Souhaitez-vous débloquer cette capacité de génération pour vos équipes ?</p>
            <a href="mailto:contact@agent.ia" class="btn">🚀 Réserver un Point Stratégique de 15 min</a>
        </div>
    </div>
</body>
</html>
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        return filename

visual_roi_generator = VisualROIGenerator()
