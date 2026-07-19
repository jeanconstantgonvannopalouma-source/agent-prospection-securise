$content = @"
"""
Module de traitement des objections
Identifie et répond aux objections de manière intelligente
"""

import logging
from typing import Dict, List, Optional, Tuple
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.models import Prospect, Objection
from database.repositories import InteractionRepository
from modules.message_engine import message_engine

logger = logging.getLogger(__name__)

class ObjectionHandler:
    """Gère les objections"""
    
    # Catégories et patterns d'objections
    OBJECTION_PATTERNS = {
        'price': [
            'cher', 'coûte', 'prix', 'budget', 'invest', 'coût', 'tarif'
        ],
        'timing': [
            'plus tard', 'pas maintenant', 'futur', 'année prochaine', 'pas urgent', 'attendre'
        ],
        'features': [
            'manquant', 'besoin', 'feature', 'fonctionnalité', 'capability', 'capacité'
        ],
        'competitor': [
            'concurrent', 'autre solution', 'meilleur', 'concurrence', 'déjà'
        ],
        'no_need': [
            'pas besoin', 'n\\'avons pas besoin', 'n\\'utilisons', 'pas intéressé'
        ]
    }
    
    @staticmethod
    def categorize_objection(text: str) -> str:
        """
        Catégorise une objection
        
        Args:
            text: Texte de l'objection
            
        Returns:
            Catégorie de l'objection
        """
        text_lower = text.lower()
        
        for category, patterns in ObjectionHandler.OBJECTION_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    logger.debug(f"Objection catégorisée: {category}")
                    return category
        
        return 'other'
    
    @staticmethod
    def get_response_strategy(category: str) -> str:
        """
        Retourne la stratégie de réponse
        
        Args:
            category: Catégorie d'objection
            
        Returns:
            Stratégie recommandée
        """
        strategies = {
            'price': "Mets en avant le ROI et le coût d'inaction",
            'timing': "Crée une urgence douce basée sur les signaux marché",
            'features': "Montre comment résoudre le besoin différemment",
            'competitor': "Explicite tes avantages compétitifs uniques",
            'no_need': "Qualifie mieux ou déplace vers future opportunity"
        }
        
        return strategies.get(category, "Reconnais et propose alternative")
    
    @staticmethod
    def analyze_objection(
        prospect: Prospect,
        objection_text: str
    ) -> Dict:
        """
        Analyse complète d'une objection
        
        Args:
            prospect: Prospect
            objection_text: Texte de l'objection
            
        Returns:
            Dictionnaire d'analyse
        """
        category = ObjectionHandler.categorize_objection(objection_text)
        strategy = ObjectionHandler.get_response_strategy(category)
        
        # Génère une réponse
        response = message_engine.generate_objection_response(
            prospect=prospect,
            objection=objection_text,
            context=f"Stratégie: {strategy}"
        )
        
        return {
            'category': category,
            'severity': 50,  # 0-100
            'strategy': strategy,
            'response': response or "Réponse non générée",
            'needs_escalation': category in ['features', 'competitor'],
        }

# Instance globale
objection_handler = ObjectionHandler()

__all__ = ['objection_handler', 'ObjectionHandler']
"@

$content | Out-File -FilePath "src\modules\objection_handler.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\modules\objection_handler.py" -ForegroundColor Green