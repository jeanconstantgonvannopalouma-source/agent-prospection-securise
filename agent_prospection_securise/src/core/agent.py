$content = @"
"""
Agent de prospection principal
Orchestre tous les modules
"""

import logging
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config
from database.connection import db
from database.repositories import ProspectRepository
from database.models import Prospect, ProspectStatus
from modules.prospect_finder import prospect_finder
from modules.message_engine import message_engine
from modules.email_sender import email_sender
from modules.objection_handler import objection_handler
from modules.analytics import analytics

logger = logging.getLogger(__name__)

class ProspectionAgent:
    """Agent principal de prospection"""
    
    def __init__(self):
        self.prospect_finder = prospect_finder
        self.message_engine = message_engine
        self.email_sender = email_sender
        self.objection_handler = objection_handler
        self.analytics = analytics
        
        logger.info("✓ ProspectionAgent initialisé")
    
    async def run_full_campaign(
        self,
        industries: List[str],
        countries: List[str],
        company_sizes: List[str]
    ) -> Dict:
        """Lance une campagne complète"""
        try:
            logger.info("🚀 Démarrage campagne complète...")
            
            # Recherche
            prospects = await self.prospect_finder.search_prospects(
                filters={
                    'industries': industries,
                    'countries': countries,
                    'company_sizes': company_sizes
                }
            )
            
            # Sauvegarde
            count = await self.prospect_finder.save_prospects(prospects)
            
            logger.info(f"✓ Campagne complète: {count} prospects")
            
            return {
                'success': True,
                'prospects_found': count,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur campagne: {e}")
            return {'success': False, 'error': str(e)}

agent = ProspectionAgent()

__all__ = ['agent', 'ProspectionAgent']
"@

$content | Out-File -FilePath "src\core\agent.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\core\agent.py" -ForegroundColor Green