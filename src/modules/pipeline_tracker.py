"""
CRM PIPELINE & SUIVI ANALYTIQUE EMBARQUÉ (SQLite)
"""
import sqlite3
import os
import time
from typing import List, Dict, Any

DB_PATH = os.path.join("data", "pipeline.db")

class PipelineTracker:
    """Gestionnaire de base de données commerciale SQLite"""

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(DB_PATH)

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE,
                company TEXT,
                position TEXT,
                industry TEXT,
                icp_score INTEGER,
                status TEXT DEFAULT 'NOUVEAU',
                estimated_deal_value REAL DEFAULT 3000.0,
                last_subject TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()

    def record_prospect(self, prospect: Dict[str, Any], subject: str = "", deal_val: float = 3000.0) -> bool:
        """Enregistre ou met à jour un prospect dans le pipeline"""
        try:
            with self._get_conn() as conn:
                conn.execute("""
                INSERT INTO prospects (first_name, last_name, email, company, position, industry, icp_score, status, estimated_deal_value, last_subject)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'CONTACTÉ', ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    status='CONTACTÉ',
                    last_subject=excluded.last_subject
                """, (
                    prospect.get("first_name", ""),
                    prospect.get("last_name", ""),
                    prospect.get("email", ""),
                    prospect.get("company", ""),
                    prospect.get("position", ""),
                    prospect.get("industry", ""),
                    prospect.get("qualification_score", 70),
                    deal_val,
                    subject
                ))
                conn.commit()
                return True
        except Exception as e:
            return False

    def update_status(self, email: str, new_status: str) -> bool:
        """Met à jour le statut (ex: 'RÉPONDU', 'RDV FIXÉ', 'GAGNÉ', 'PERDU')"""
        with self._get_conn() as conn:
            cur = conn.execute("UPDATE prospects SET status = ? WHERE email = ?", (new_status, email))
            conn.commit()
            return cur.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """Calcule les statistiques globales du pipeline de prospection"""
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            total_prospects = conn.execute("SELECT COUNT(*) FROM prospects").fetchone()[0]
            contacted = conn.execute("SELECT COUNT(*) FROM prospects WHERE status = 'CONTACTÉ'").fetchone()[0]
            won = conn.execute("SELECT COUNT(*) FROM prospects WHERE status = 'GAGNÉ'").fetchone()[0]
            pipeline_val = conn.execute("SELECT SUM(estimated_deal_value) FROM prospects WHERE status != 'PERDU'").fetchone()[0] or 0.0

            rows = conn.execute("SELECT * FROM prospects ORDER BY id DESC LIMIT 5").fetchall()
            recent = [dict(r) for r in rows]

            return {
                "total_prospects": total_prospects,
                "contacted_count": contacted,
                "deals_won": won,
                "total_pipeline_value_eur": round(pipeline_val, 2),
                "recent_prospects": recent
            }

pipeline_tracker = PipelineTracker()
