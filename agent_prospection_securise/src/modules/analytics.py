$content = @"
"""
Module d'analytics et reporting
Métriques et performances
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.connection import db
from database.repositories import ProspectRepository
from database.models import Prospect, ProspectStatus, Message, MessageStatus

logger = logging.getLogger(__name__)

class Analytics:
    """Analytics et reporting"""
    
    @staticmethod
    def get_dashboard_stats() -> Dict:
        """Retourne les stats du dashboard"""
        session = None
        try:
            session = db.get_session()
            repo = ProspectRepository(session)
            
            total = repo.count()
            new = repo.count_by_status(ProspectStatus.NEW)
            contacted = repo.count_by_status(ProspectStatus.CONTACTED)
            qualified = repo.count_by_status(ProspectStatus.QUALIFIED)
            won = repo.count_by_status(ProspectStatus.WON)
            
            conversion_rate = (won / total * 100) if total > 0 else 0
            
            return {
                'total_prospects': total,
                'new': new,
                'contacted': contacted,
                'qualified': qualified,
                'won': won,
                'conversion_rate': round(conversion_rate, 2),
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur stats: {e}")
            return {}
        finally:
            if session:
                db.close_session(session)
    
    @staticmethod
    def get_conversion_stats() -> Dict:
        """Retourne les stats de conversion"""
        try:
            stats = {
                'total_contacted': 0,
                'total_responses': 0,
                'total_conversions': 0,
                'response_rate': 0,
                'conversion_rate': 0,
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur stats conversion: {e}")
            return {}
    
    @staticmethod
    def get_email_stats() -> Dict:
        """Retourne les stats d'email"""
        try:
            stats = {
                'total_sent': 0,
                'total_opened': 0,
                'total_clicked': 0,
                'open_rate': 0,
                'click_rate': 0,
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur stats email: {e}")
            return {}

analytics = Analytics()

__all__ = ['analytics', 'Analytics']
"@

$content | Out-File -FilePath "src\modules\analytics.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\modules\analytics.py" -ForegroundColor Green