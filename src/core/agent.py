"""Agent de prospection principal"""
import logging
import asyncio
from typing import Dict, List
from datetime import datetime

from database.connection import init_db
from database.repositories import ProspectRepository
from database.models import ProspectStatus
from modules.prospect_finder import prospect_finder
from modules.message_engine import message_engine
from modules.analytics import analytics
from config import config

logger = logging.getLogger(__name__)

class ProspectionAgent:
    """Agent principal de prospection"""
    
    def __init__(self):
        self.db = init_db(config.DATABASE_URL)
        self.prospect_finder = prospect_finder
        self.message_engine = message_engine
        self.analytics = analytics
        
        logger.info("ProspectionAgent init")
    
    async def run_full_campaign(self, industries: List[str], 
                                countries: List[str], 
                                company_sizes: List[str] = None) -> Dict:
        """Lance une campagne complète"""
        try:
            logger.info("Campaign start")
            
            prospects = await self.prospect_finder.search_prospects(
                filters={
                    'industries': industries,
                    'countries': countries,
                    'company_sizes': company_sizes or ['10-50', '50-200']
                },
                limit=50
            )
            
            count = await self.prospect_finder.save_prospects(
                prospects, 
                self.db, 
                ProspectRepository
            )
            
            return {
                'success': True,
                'prospects_found': count,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Campaign error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_daily_workflow(self) -> Dict:
        """Lance le workflow quotidien"""
        try:
            logger.info("Daily workflow start")
            
            session = None
            try:
                session = self.db.get_session()
                repo = ProspectRepository(session)
                
                prospects = repo.find_by_status(ProspectStatus.NEW)
                
                contacted_count = 0
                
                for prospect in prospects[:10]:
                    message = self.message_engine.generate_personalized_message(
                        prospect=prospect,
                        pain_points=['Acquisition', 'ROI'],
                        solution='AI Platform',
                        tone='professionnel'
                    )
                    
                    if message:
                        repo.update_status(prospect.id, ProspectStatus.CONTACTED)
                        contacted_count += 1
                
                return {
                    'success': True,
                    'emails_sent': contacted_count,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            finally:
                if session:
                    self.db.close_session(session)
                
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            return {'success': False, 'error': str(e)}

agent = ProspectionAgent()
