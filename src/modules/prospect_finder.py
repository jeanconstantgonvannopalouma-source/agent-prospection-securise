"""Module de recherche et enrichissement de prospects"""
import logging
from typing import List, Dict, Optional
import asyncio
import random

from security.validation import validator
from database.models import ProspectStatus

logger = logging.getLogger(__name__)

class ProspectFinder:
    """Recherche et enrichissement de prospects"""
    
    def __init__(self):
        # Données de test
        self.mock_prospects = [
            {
                'name': 'John Doe',
                'email': 'john.doe@techcorp.fr',
                'company': 'TechCorp France',
                'position': 'Directeur Commercial',
                'country': 'FR',
                'industry': 'Tech',
            },
            {
                'name': 'Marie Dubois',
                'email': 'marie.dubois@startupai.fr',
                'company': 'StartupAI',
                'position': 'Head of Sales',
                'country': 'FR',
                'industry': 'SaaS',
            },
            {
                'name': 'Pierre Martin',
                'email': 'pierre.martin@software.com',
                'company': 'Software Solutions',
                'position': 'VP Sales',
                'country': 'FR',
                'industry': 'Software',
            },
            {
                'name': 'Sophie Laurent',
                'email': 'sophie.laurent@consulting.fr',
                'company': 'Digital Consulting',
                'position': 'Directeur Général',
                'country': 'FR',
                'industry': 'Consulting',
            },
        ]
    
    async def search_prospects(self, filters: Dict = None, limit: int = 50) -> List[Dict]:
        """Recherche de prospects"""
        try:
            logger.info(f"🔍 Recherche prospects (limit: {limit})...")
            
            # Filtre
            if limit > 500:
                limit = 500
            
            results = self.mock_prospects[:limit]
            
            logger.info(f"✓ {len(results)} prospects trouvés")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche: {e}")
            return []
    
    async def enrich_prospect(self, prospect_data: Dict) -> Optional[Dict]:
        """Enrichit les données d'un prospect"""
        try:
            # Valide email
            if not validator.validate_email(prospect_data.get('email', '')):
                logger.warning(f"Email invalide")
                return None
            
            # Nettoie les données
            name_parts = prospect_data.get('name', '').split()
            prospect_data['first_name'] = name_parts[0] if name_parts else 'Unknown'
            prospect_data['last_name'] = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            prospect_data['job_title'] = prospect_data.get('position', '')
            
            # Ajoute un score de qualification initial
            prospect_data['qualification_score'] = random.randint(40, 95)
            prospect_data['conversion_probability'] = prospect_data['qualification_score'] / 100.0
            
            return prospect_data
            
        except Exception as e:
            logger.error(f"❌ Erreur enrichissement: {e}")
            return None
    
    async def save_prospects(self, prospects: List[Dict], db, ProspectRepository) -> int:
        """Sauvegarde les prospects en BD"""
        count = 0
        
        for prospect_data in prospects:
            session = None
            try:
                session = db.get_session()
                repo = ProspectRepository(session)
                
                # Enrichit
                enriched = await self.enrich_prospect(prospect_data)
                if not enriched:
                    continue
                
                # Crée
                prospect = repo.create(enriched)
                if prospect:
                    count += 1
                    logger.info(f"✓ Prospect sauvegardé: {prospect.email}")
                
            except Exception as e:
                logger.error(f"❌ Erreur sauvegarde: {e}")
                continue
            finally:
                if session:
                    db.close_session(session)
        
        logger.info(f"✓ {count} prospects sauvegardés")
        return count
    
    async def score_prospect(self, prospect, interactions_count: int = 0, 
                            email_opens: int = 0, responses: int = 0) -> tuple:
        """Calcule le score de qualification"""
        try:
            score = 50
            
            # Décideurs +20
            if 'Directeur' in prospect.job_title or 'VP' in prospect.job_title:
                score += 20
            
            # Interactions: +2 par interaction
            score += min(interactions_count * 2, 20)
            
            # Email opens: +1 par ouverture
            score += min(email_opens * 1, 10)
            
            # Réponses: +5 par réponse
            score += min(responses * 5, 20)
            
            score = max(0, min(100, score))
            conversion_prob = score / 100.0
            
            logger.debug(f"Score: {score}/100")
            
            return score, conversion_prob
            
        except Exception as e:
            logger.error(f"❌ Erreur scoring: {e}")
            return 50, 0.5

# Instance globale
prospect_finder = ProspectFinder()
