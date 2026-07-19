$content = @"
"""
Module de workflows automatisés
Gère les flux de prospection automatisés
"""

import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.connection import db
from database.repositories import ProspectRepository, MessageRepository
from database.models import Prospect, ProspectStatus, Message, MessageStatus
from modules.message_engine import message_engine
from modules.email_sender import email_sender
from security.sanitizer import DataSanitizer

logger = logging.getLogger(__name__)
sanitizer = DataSanitizer()

class WorkflowStep(Enum):
    """Étapes possibles d'un workflow"""
    SEARCH = "recherche"
    ENRICH = "enrichissement"
    SCORE = "scoring"
    MESSAGE_DRAFT = "brouillon_message"
    SEND_MESSAGE = "envoi_message"
    WAIT = "attente"
    QUALIFY = "qualification"
    PRESENT = "présentation"
    CLOSE = "fermeture"

class WorkflowManager:
    """Gère les workflows automatisés"""
    
    def __init__(self):
        self.workflows = {}
        logger.info("✓ WorkflowManager initialisé")
    
    async def run_daily_workflow(self) -> Dict:
        """
        Lance le workflow quotidien
        
        Returns:
            Résumé de l'exécution
        """
        try:
            logger.info("📅 Démarrage workflow quotidien...")
            
            session = None
            try:
                session = db.get_session()
                repo = ProspectRepository(session)
                
                # Récupère les prospects à contacter
                prospects = repo.find_by_status(ProspectStatus.NEW, limit=50)
                
                contacted_count = 0
                
                for prospect in prospects:
                    # Génère un message
                    message = message_engine.generate_personalized_message(
                        prospect=prospect,
                        pain_points=['Acquisition clients difficile', 'ROI incertain'],
                        solution='Notre plateforme IA aide à trouver et convertir les clients',
                        tone='professionnel'
                    )
                    
                    if message:
                        # Envoie l'email
                        success, msg = email_sender.send_email(
                            to_email=prospect.email,
                            subject=f"Idée pour {prospect.company_name}",
                            body=message
                        )
                        
                        if success:
                            contacted_count += 1
                            # Met à jour le statut
                            repo.update_status(prospect.id, ProspectStatus.CONTACTED)
                            logger.info(f"✓ Email envoyé: {prospect.email}")
                        
                        # Pause entre envois
                        await asyncio.sleep(2)
                
                logger.info(f"✓ Workflow quotidien: {contacted_count} emails envoyés")
                
                return {
                    'success': True,
                    'emails_sent': contacted_count,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            finally:
                if session:
                    db.close_session(session)
                
        except Exception as e:
            logger.error(f"❌ Erreur workflow quotidien: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_follow_up_workflow(self) -> Dict:
        """Workflow de relance"""
        try:
            logger.info("📧 Workflow de relance...")
            
            session = None
            try:
                session = db.get_session()
                repo = ProspectRepository(session)
                
                # Prospects contactés il y a 3 jours
                three_days_ago = datetime.utcnow() - timedelta(days=3)
                
                # Récupère les prospects
                prospects = repo.find_by_status(ProspectStatus.CONTACTED, limit=30)
                
                relance_count = 0
                
                for prospect in prospects:
                    if prospect.last_contacted and prospect.last_contacted < three_days_ago:
                        message = message_engine.generate_personalized_message(
                            prospect=prospect,
                            pain_points=['Suivi important'],
                            solution='Relance personnalisée',
                            tone='amical'
                        )
                        
                        if message:
                            subject = f"Suivi: {prospect.company_name}"
                            success, msg = email_sender.send_email(
                                to_email=prospect.email,
                                subject=subject,
                                body=message
                            )
                            
                            if success:
                                relance_count += 1
                                logger.info(f"✓ Relance envoyée: {prospect.email}")
                        
                        await asyncio.sleep(1)
                
                logger.info(f"✓ Workflow relance: {relance_count} relances")
                
                return {
                    'success': True,
                    'follow_ups_sent': relance_count,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            finally:
                if session:
                    db.close_session(session)
                
        except Exception as e:
            logger.error(f"❌ Erreur workflow relance: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_qualification_workflow(self) -> Dict:
        """Workflow de qualification"""
        try:
            logger.info("🎯 Workflow de qualification...")
            
            session = None
            try:
                session = db.get_session()
                repo = ProspectRepository(session)
                
                # Prospects avec interactions
                prospects = repo.find_by_status(ProspectStatus.CONTACTED, limit=20)
                
                qualified_count = 0
                
                for prospect in prospects:
                    # Évalue le score
                    if prospect.qualification_score >= 70:
                        repo.update_status(prospect.id, ProspectStatus.QUALIFIED)
                        qualified_count += 1
                        logger.info(f"✓ Prospect qualifié: {prospect.email} (score: {prospect.qualification_score})")
                
                logger.info(f"✓ Workflow qualification: {qualified_count} qualifiés")
                
                return {
                    'success': True,
                    'qualified': qualified_count,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            finally:
                if session:
                    db.close_session(session)
                
        except Exception as e:
            logger.error(f"❌ Erreur qualification: {e}")
            return {'success': False, 'error': str(e)}

workflow_manager = WorkflowManager()

__all__ = ['workflow_manager', 'WorkflowManager', 'WorkflowStep']
"@

$content | Out-File -FilePath "src\core\workflow.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\core\workflow.py" -ForegroundColor Green