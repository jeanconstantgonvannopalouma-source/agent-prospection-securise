"""Moteur de génération de messages"""
import logging
from typing import Dict, Optional
import re

logger = logging.getLogger(__name__)

class MessageEngine:
    """Génération de messages personnalisés"""
    
    def __init__(self):
        self.pain_point_responses = {
            'acquisition': 'Notre plateforme aide à identifier les meilleurs prospects',
            'conversion': 'Nous augmentons votre taux de conversion avec l\'IA',
            'roi': 'Vous verrez un ROI de 300% en moins de 6 mois',
            'temps': 'Gagnez 10h par semaine sur la prospection',
        }
    
    def generate_personalized_message(self, prospect, pain_points: list, 
                                     solution: str, tone: str = "professionnel") -> Optional[str]:
        """Génère un message hyper-personnalisé"""
        try:
            logger.info(f"📝 Génération message pour {prospect.email}")
            
            # Template adapté
            message = f"""Bonjour {prospect.first_name},

J'ai remarqué que {prospect.company_name} est dans le secteur {prospect.industry}.

Nous aidons les entreprises comme la vôtre à:
- Trouver les bons prospects rapidement
- Augmenter le taux de conversion
- Réduire le coût d'acquisition client

Auriez-vous 15 minutes cette semaine pour en discuter?

Cordialement,
L'équipe Agent Prospection"""
            
            logger.info(f"✓ Message généré ({len(message)} caractères)")
            return message
            
        except Exception as e:
            logger.error(f"❌ Erreur génération: {e}")
            return None
    
    def generate_objection_response(self, prospect, objection: str, context: str = "") -> Optional[str]:
        """Génère une réponse à une objection"""
        try:
            logger.info(f"Réponse à objection: {objection[:50]}")
            
            response = f"""J'ai bien compris votre préoccupation concernant: {objection}

Voici comment nous répondons à cette objection:
- Solution 1: Adaptabilité complète à vos besoins
- Solution 2: Essai gratuit pendant 30 jours
- Solution 3: Support dédié inclus

Quand pourrions-nous faire un point?"""
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur réponse: {e}")
            return None
    
    def analyze_message_quality(self, message: str) -> Dict:
        """Analyse la qualité d'un message"""
        analysis = {
            'length': len(message),
            'word_count': len(message.split()),
            'has_cta': bool(re.search(r'(disponible|rendez-vous|appel|réunion)', message, re.I)),
            'has_personalization': bool(re.search(r'(votre|vos|vous)', message, re.I)),
            'has_urgency': bool(re.search(r'(rapide|urgent|cette semaine)', message, re.I)),
        }
        
        quality_score = 0
        if analysis['length'] > 100:
            quality_score += 20
        if analysis['has_cta']:
            quality_score += 25
        if analysis['has_personalization']:
            quality_score += 20
        if analysis['has_urgency']:
            quality_score += 15
        
        analysis['quality_score'] = min(100, quality_score)
        
        return analysis

# Instance globale
message_engine = MessageEngine()
