"""Routes API REST"""
import logging
from typing import Dict
import asyncio
from datetime import datetime

from config import config
from database.connection import init_db
from database.repositories import ProspectRepository, MessageRepository
from database.models import ProspectStatus
from core.agent import agent
from modules.analytics import analytics

logger = logging.getLogger(__name__)

class APIRoutes:
    """Routes API REST"""
    
    def __init__(self):
        self.db = init_db(config.DATABASE_URL)
    
    # ===== PROSPECTS =====
    
    def create_prospect(self, data: Dict) -> tuple:
        """POST /prospects"""
        session = None
        try:
            session = self.db.get_session()
            repo = ProspectRepository(session)
            
            prospect = repo.create(data)
            
            return {
                'success': True,
                'prospect_id': prospect.id,
                'email': prospect.email,
                'message': f'Prospect créé: {prospect.email}'
            }, 201
            
        except Exception as e:
            logger.error(f"Erreur création: {e}")
            return {'error': str(e)}, 400
        finally:
            if session:
                self.db.close_session(session)
    
    def get_prospect(self, prospect_id: int) -> tuple:
        """GET /prospects/{id}"""
        session = None
        try:
            session = self.db.get_session()
            repo = ProspectRepository(session)
            
            prospect = repo.get_by_id(prospect_id)
            
            if not prospect:
                return {'error': 'Prospect non trouvé'}, 404
            
            return {
                'success': True,
                'prospect': prospect.to_dict()
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur requête: {e}")
            return {'error': str(e)}, 400
        finally:
            if session:
                self.db.close_session(session)
    
    def list_prospects(self, limit: int = 50, offset: int = 0) -> tuple:
        """GET /prospects"""
        session = None
        try:
            session = self.db.get_session()
            repo = ProspectRepository(session)
            
            prospects = repo.get_all(limit=limit)
            total = repo.count()
            
            return {
                'success': True,
                'total': total,
                'count': len(prospects),
                'prospects': [p.to_dict() for p in prospects]
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur listage: {e}")
            return {'error': str(e)}, 400
        finally:
            if session:
                self.db.close_session(session)
    
    def update_prospect(self, prospect_id: int, data: Dict) -> tuple:
        """PUT /prospects/{id}"""
        session = None
        try:
            session = self.db.get_session()
            repo = ProspectRepository(session)
            
            success = repo.update_status(prospect_id, ProspectStatus.CONTACTED)
            
            if not success:
                return {'error': 'Prospect non trouvé'}, 404
            
            return {'success': True, 'message': 'Prospect mis à jour'}, 200
            
        except Exception as e:
            logger.error(f"Erreur mise à jour: {e}")
            return {'error': str(e)}, 400
        finally:
            if session:
                self.db.close_session(session)
    
    # ===== MESSAGES =====
    
    def generate_message(self, prospect_id: int, pain_points: list) -> tuple:
        """POST /messages/generate"""
        session = None
        try:
            session = self.db.get_session()
            repo = ProspectRepository(session)
            
            prospect = repo.get_by_id(prospect_id)
            if not prospect:
                return {'error': 'Prospect non trouvé'}, 404
            
            from modules.message_engine import message_engine
            message = message_engine.generate_personalized_message(
                prospect=prospect,
                pain_points=pain_points,
                solution='Notre solution aide a acquerir les clients',
                tone='professionnel'
            )
            
            if not message:
                return {'error': 'Impossible générer message'}, 500
            
            return {
                'success': True,
                'message': message
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur génération: {e}")
            return {'error': str(e)}, 400
        finally:
            if session:
                self.db.close_session(session)
    
    # ===== CAMPAIGNS =====
    
    async def run_campaign(self, industries: list, countries: list) -> tuple:
        """POST /campaigns/run"""
        try:
            result = await agent.run_full_campaign(
                industries=industries,
                countries=countries,
                company_sizes=['10-50', '50-200']
            )
            
            status = 200 if result['success'] else 500
            return {
                'success': result['success'],
                'prospects': result.get('prospects_found', 0),
                'timestamp': result.get('timestamp')
            }, status
            
        except Exception as e:
            logger.error(f"Erreur campagne: {e}")
            return {'error': str(e)}, 400
    
    async def run_daily_workflow(self) -> tuple:
        """POST /workflows/daily"""
        try:
            result = await agent.run_daily_workflow()
            
            status = 200 if result['success'] else 500
            return {
                'success': result['success'],
                'emails_sent': result.get('emails_sent', 0),
                'timestamp': result.get('timestamp')
            }, status
            
        except Exception as e:
            logger.error(f"Erreur workflow: {e}")
            return {'error': str(e)}, 400
    
    # ===== ANALYTICS =====
    
    def get_stats(self) -> tuple:
        """GET /stats"""
        try:
            from database.models import ProspectStatus
            stats = analytics.get_dashboard_stats(self.db, ProspectRepository, ProspectStatus)
            
            return {
                'success': True,
                'stats': stats
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur stats: {e}")
            return {'error': str(e)}, 400
    
    # ===== HEALTH =====
    
    def health_check(self) -> tuple:
        """GET /health"""
        try:
            is_healthy = self.db.health_check()
            
            status_text = 'healthy' if is_healthy else 'unhealthy'
            db_status = 'ok' if is_healthy else 'error'
            timestamp_str = datetime.utcnow().isoformat()
            
            return {
                'status': status_text,
                'database': db_status,
                'timestamp': timestamp_str
            }, 200 if is_healthy else 503
            
        except Exception as e:
            logger.error(f"Erreur health: {e}")
            return {'error': str(e), 'status': 'error'}, 503

api_routes = APIRoutes()
