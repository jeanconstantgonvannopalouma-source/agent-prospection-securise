"""Module d'analytics et reporting"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class Analytics:
    """Analytics et statistiques"""
    
    def __init__(self):
        pass
    
    @staticmethod
    def get_dashboard_stats(db, ProspectRepository, ProspectStatus) -> Dict:
        """Retourne les stats du dashboard"""
        session = None
        try:
            session = db.get_session()
            repo = ProspectRepository(session)
            
            total = repo.count()
            new = repo.count_by_status(ProspectStatus.NEW)
            contacted = repo.count_by_status(ProspectStatus.CONTACTED)
            qualified = repo.count_by_status(ProspectStatus.QUALIFIED)
            
            conversion_rate = 0
            if total > 0:
                conversion_rate = round((qualified / total) * 100, 2)
            
            stats = {
                'total_prospects': total,
                'new': new,
                'contacted': contacted,
                'qualified': qualified,
                'conversion_rate': conversion_rate,
            }
            
            logger.info(f"Stats: Total={total}, New={new}, Contacted={contacted}")
            return stats
            
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
            logger.error(f"❌ Erreur conversion stats: {e}")
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
            logger.error(f"❌ Erreur email stats: {e}")
            return {}

analytics = Analytics()
