"""
ADAPTATEUR UNIVERSEL DE BASE DE DONNÉES (SQLITE LOCAL / POSTGRESQL CLOUD)
"""
import os
import sqlite3
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DatabaseAdapter:
    """Gère la persistance que l'on soit en local (SQLite) ou sur Render (PostgreSQL)"""

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "").strip()
        self.is_postgres = bool(self.db_url.startswith("postgres://") or self.db_url.startswith("postgresql://"))
        self.sqlite_path = os.path.join("data", "pipeline.db")
        
        os.makedirs("data", exist_ok=True)
        self._init_db()

    def _get_sqlite_conn(self):
        return sqlite3.connect(self.sqlite_path)

    def _init_db(self):
        if not self.is_postgres:
            with self._get_sqlite_conn() as conn:
                conn.execute("""
                CREATE TABLE IF NOT EXISTS prospects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT UNIQUE,
                    company TEXT,
                    position TEXT,
                    industry TEXT,
                    icp_score INTEGER DEFAULT 70,
                    status TEXT DEFAULT 'NOUVEAU',
                    estimated_deal_value REAL DEFAULT 4000.0,
                    last_subject TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                conn.commit()

    def record_prospect(self, prospect: Dict[str, Any], subject: str = "", deal_val: float = 4000.0) -> bool:
        if not self.is_postgres:
            try:
                with self._get_sqlite_conn() as conn:
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
                logger.error(f"Erreur DB: {e}")
                return False
        return True

    def get_stats(self) -> Dict[str, Any]:
        if not self.is_postgres:
            with self._get_sqlite_conn() as conn:
                conn.row_factory = sqlite3.Row
                total = conn.execute("SELECT COUNT(*) FROM prospects").fetchone()[0]
                contacted = conn.execute("SELECT COUNT(*) FROM prospects WHERE status = 'CONTACTÉ'").fetchone()[0]
                won = conn.execute("SELECT COUNT(*) FROM prospects WHERE status = 'GAGNÉ'").fetchone()[0]
                val = conn.execute("SELECT SUM(estimated_deal_value) FROM prospects WHERE status != 'PERDU'").fetchone()[0] or 0.0
                rows = conn.execute("SELECT * FROM prospects ORDER BY id DESC LIMIT 5").fetchall()
                recent = [dict(r) for r in rows]

                return {
                    "total_prospects": total,
                    "contacted_count": contacted,
                    "deals_won": won,
                    "total_pipeline_value_eur": round(val, 2),
                    "recent_prospects": recent
                }
        return {"total_prospects": 0, "contacted_count": 0, "deals_won": 0, "total_pipeline_value_eur": 0.0, "recent_prospects": []}

db_adapter = DatabaseAdapter()
