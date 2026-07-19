$content = @"
"""
Routes API REST
Endpoints pour l'application
"""

import logging
from typing import Dict, List
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config
from logging_config import logger
from database.connection import db
from database.repositories import ProspectRepository, MessageRepository
from database.models import Prospect, ProspectStatus
from api.schemas import ProspectCreate, ProspectUpdate, SearchRequest
from api.middleware import require_auth, rate_limit, validate_input, SecurityHeaders
from modules.prospect_finder import prospect_finder
from modules.message_engine import message_engine
from modules.analytics import analytics
from core.agent import agent
from core.workflow import workflow_manager

class APIRoutes:
    """Toutes les routes API"""
    
    # ===== PROSPECTS =====
    
    @staticmethod
    @rate_limit('email')
    def create_prospect(data: Dict) -> tuple:
        """POST /prospects"""
        session = None
        try:
            session = db.get_session()
            repo = ProspectRepository(session)
            
            prospect = repo.create(data)
            
            return {
                'success': True,
                'prospect_id': prospect.id,
                'email': prospect.email,
                'message': f'Prospect créé: {prospect.email}'
            }, 201
            
        except Exception as e:
            logger.error(f"❌ Erreur création prospect: {e}")
            return {'error': str(e)}, 400
        finally:
            if session:
                db.close_session(session)
    
    @staticmethod
    def get_prospect(prospect_id: int) -> tuple:
        """GET /prospects/{id}"""
        session = None
        try:
            session = db.get_session()
            repo = ProspectRepository(session)
            
            prospect = repo.get_by_id(prospect_id)
            
            if not prospect:
                return {'error': 'Prospect non trouvé'}, 404
            
            return {
                'success': True,
                'prospect': prospect.to_dict()
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Erreur requête prospect: {e}")
            return {'error': str(e)}, 400
        finally:
            if session:
                db.close_session(session)
    
    @staticmethod
    def list_prospects(limit: int = 50, offset: int = 0) -> tuple:
        """GET /prospects"""
        session = None
        try:
            session = db.get_session()
            repo = ProspectRepository(session)
            
            prospects = repo.get_all(limit=limit, offset=offset)
            total = repo.count()
            
            return {
                'success': True,
                'total': total,
                'count': len(prospects),
                'prospects': [p.to_dict() for p in prospects]
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Erreur listage: {e}")
            return {'error': str(e)}, 400
        finally:
            if session:
                db.close_session(session)
    
    @staticmethod
    def update_prospect(prospect_id: int, data: Dict) -> tuple:
        """PUT /prospects/{id}"""
        session = None
        try:
            session = db.get_session()
            repo = ProspectRepository(session)
            
            success = repo.update_contact_info(prospect_id, **data)
            
            if not success:
                return {'error': 'Prospect non trouvé'}, 404
            
            return {
                'success': True,
                'message': 'Prospect mis à jour'
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour: {e}")
            return {'error': str(e)}, 400
        finally:
            if session:
                db.close_session(session)
    
    # ===== RECHERCHE =====
    
    @staticmethod
    async def search_prospects_api(filters: Dict) -> tuple:
        """POST /search"""
        try:
            prospects = await prospect_finder.search_prospects(
                filters=filters,
                limit=filters.get('limit', 50)
            )
            
            count = await prospect_finder.save_prospects(prospects)
            
            return {
                'success': True,
                'found': len(prospects),
                'saved': count
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche: {e}")
            return {'error': str(e)}, 400
    
    # ===== MESSAGES =====
    
    @staticmethod
    def generate_message(prospect_id: int, pain_points: List[str]) -> tuple:
        """POST /messages/generate"""
        session = None
        try:
            session = db.get_session()
            repo = ProspectRepository(session)
            
            prospect = repo.get_by_id(prospect_id)
            if not prospect:
                return {'error': 'Prospect non trouvé'}, 404
            
            message = message_engine.generate_personalized_message(
                prospect=prospect,
                pain_points=pain_points,
                solution='Notre solution aide à acquérir et convertir les clients',
                tone='professionnel'
            )
            
            if not message:
                return {'error': 'Impossible générer message'}, 500
            
            return {
                'success': True,
                'message': message
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Erreur génération message: {e}")
            return {'error': str(e)}, 400
        finally:
            if session:
                db.close_session(session)
    
    # ===== CAMPAIGNS =====
    
    @staticmethod
    async def run_campaign(industries: List[str], countries: List[str]) -> tuple:
        """POST /campaigns/run"""
        try:
            result = await agent.run_full_campaign(
                industries=industries,
                countries=countries,
                company_sizes=['10-50', '50-200']
            )
            
            return {
                'success': result['success'],
                'prospects': result.get('prospects_found', 0),
                'timestamp': result.get('timestamp')
            }, 200 if result['success'] else 500
            
        except Exception as e:
            logger.error(f"❌ Erreur campagne: {e}")
            return {'error': str(e)}, 400
    
    @staticmethod
    async def run_daily_workflow() -> tuple:
        """POST /workflows/daily"""
        try:
            result = await workflow_manager.run_daily_workflow()
            
            return {
                'success': result['success'],
                'emails_sent': result.get('emails_sent', 0),
                'timestamp': result.get('timestamp')
            }, 200 if result['success'] else 500
            
        except Exception as e:
            logger.error(f"❌ Erreur workflow: {e}")
            return {'error': str(e)}, 400
    
    # ===== ANALYTICS =====
    
    @staticmethod
    def get_stats() -> tuple:
        """GET /stats"""
        try:
            stats = analytics.get_dashboard_stats()
            
            return {
                'success': True,
                'stats': stats
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Erreur stats: {e}")
            return {'error': str(e)}, 400
    
    # ===== HEALTH =====
    
    @staticmethod
    def health_check() -> tuple:
        """GET /health"""
        try:
            db_healthy = db.health_check()
            
            return {
                'status': 'healthy' if db_healthy else 'unhealthy',
                'database': 'ok' if db_healthy else 'error',
                'timestamp': datetime.utcnow().isoformat()
            }, 200 if db_healthy else 503
            
        except Exception as e:
            logger.error(f"❌ Erreur health check: {e}")
            return {'error': str(e)}, 503

api_routes = APIRoutes()

__all__ = ['api_routes', 'APIRoutes']
"@

$content | Out-File -FilePath "src\api\routes.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\api\routes.py" -ForegroundColor Green