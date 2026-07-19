$content = @"
"""
Moteur de génération de messages personnalisés avec GPT-4
Crée des messages ultra-personnalisés et persuasifs
"""

import logging
from typing import List, Dict, Optional, Tuple
import sys
from pathlib import Path
from datetime import datetime
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config
from security.sanitizer import DataSanitizer
from database.models import Prospect, Message, MessageStatus
from database.repositories import MessageRepository

logger = logging.getLogger(__name__)
sanitizer = DataSanitizer()

class MessageEngine:
    """Génération de messages avec GPT-4"""
    
    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        self.model = config.OPENAI_MODEL
        self.max_retries = config.OPENAI_MAX_RETRIES
        self.timeout = config.OPENAI_TIMEOUT
        
        if not self.api_key:
            logger.warning("⚠️ OpenAI API key non configurée")
        else:
            logger.info(f"✓ Message Engine initialisé (model: {self.model})")
    
    def generate_personalized_message(
        self,
        prospect: Prospect,
        pain_points: List[str],
        solution: str,
        tone: str = "professionnel"
    ) -> Optional[str]:
        """
        Génère un message hyper-personnalisé avec GPT-4
        
        Args:
            prospect: Prospect cible
            pain_points: Points de douleur identifiés
            solution: Solution à proposer
            tone: Ton du message
            
        Returns:
            Message généré ou None
        """
        try:
            # Construit le prompt
            prompt = self._build_prompt(prospect, pain_points, solution, tone)
            
            # Appelle GPT-4
            message_text = self._call_openai(prompt)
            
            if not message_text:
                logger.warning("❌ Aucun message généré par GPT-4")
                return None
            
            # Nettoie et valide
            message_text = sanitizer.sanitize_string(message_text)
            
            logger.info(f"✓ Message généré pour {prospect.email}")
            return message_text
            
        except Exception as e:
            logger.error(f"❌ Erreur génération message: {e}")
            return None
    
    def generate_objection_response(
        self,
        prospect: Prospect,
        objection: str,
        context: str = ""
    ) -> Optional[str]:
        """
        Génère une réponse à une objection
        
        Args:
            prospect: Prospect
            objection: Objection reçue
            context: Contexte supplémentaire
            
        Returns:
            Réponse générée
        """
        try:
            prompt = f"""
            Tu es un expert en vente B2B.
            
            Prospect: {prospect.first_name} {prospect.last_name} de {prospect.company_name}
            Position: {prospect.job_title}
            Secteur: {prospect.industry}
            
            Objection reçue: "{objection}"
            
            Contexte: {context}
            
            Génère une réponse courte, convaincante et professionnelle qui:
            1. Reconnaît l'objection
            2. Fournit une contre-argumentation basée sur des chiffres
            3. Propose une alternative
            
            Réponds en moins de 150 mots.
            """
            
            response = self._call_openai(prompt)
            
            if response:
                response = sanitizer.sanitize_string(response)
                logger.info(f"✓ Réponse générée pour objection")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur génération réponse: {e}")
            return None
    
    def _build_prompt(
        self,
        prospect: Prospect,
        pain_points: List[str],
        solution: str,
        tone: str
    ) -> str:
        """Construit le prompt pour GPT-4"""
        
        pain_points_text = "\\n".join([f"- {p}" for p in pain_points])
        
        prompt = f"""
        Tu es un expert en prospection B2B hyper-performant.
        
        Tu dois rédiger un email de prospection ULTRA-PERSONNALISÉ pour cette personne:
        
        NOM: {prospect.first_name} {prospect.last_name}
        ENTREPRISE: {prospect.company_name}
        POSITION: {prospect.job_title}
        SECTEUR: {prospect.industry}
        TAILLE ENTREPRISE: {prospect.company_size}
        PAYS: {prospect.country}
        
        POINTS DE DOULEUR IDENTIFIÉS:
        {pain_points_text}
        
        NOTRE SOLUTION:
        {solution}
        
        STYLE DEMANDÉ:
        - Ton: {tone}
        - Longueur: 100-150 mots maximum
        - Impact: Référence spécifique au rôle/secteur
        - CTA: Proposer un entretien de 15 minutes
        - Créativité: Unique et mémorable
        
        IMPORTANT:
        - Pas de formules génériques
        - Pas d'emojis
        - Authentique et personnel
        - Inclure 1 statistique pertinente
        - Inclure 1 preuve sociale
        - Créer une urgence douce (pas invasive)
        
        Réponds UNIQUEMENT avec le texte de l'email, prêt à envoyer.
        """
        
        return prompt.strip()
    
    def _call_openai(self, prompt: str) -> Optional[str]:
        """
        Appelle l'API OpenAI (avec retry)
        
        Args:
            prompt: Prompt pour GPT-4
            
        Returns:
            Réponse générée ou None
        """
        if not self.api_key:
            logger.error("❌ API key OpenAI manquante")
            return None
        
        try:
            import openai
            openai.api_key = self.api_key
            
            # Appelle GPT-4 avec retry
            for attempt in range(self.max_retries):
                try:
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "Tu es un expert en prospection B2B."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=500,
                        timeout=self.timeout
                    )
                    
                    return response.choices[0].message.content.strip()
                    
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"⚠️ Tentative {attempt + 1} échouée: {e}")
                        import time
                        time.sleep(2 ** attempt)
                    else:
                        raise
        
        except ImportError:
            logger.error("❌ openai library non installée")
        except Exception as e:
            logger.error(f"❌ Erreur appel OpenAI: {e}")
        
        return None
    
    def analyze_message_quality(self, message: str) -> Dict:
        """
        Analyse la qualité d'un message
        
        Args:
            message: Texte du message
            
        Returns:
            Dictionnaire d'analyse
        """
        analysis = {
            'length': len(message),
            'word_count': len(message.split()),
            'has_cta': bool(re.search(r'(calendly|appel|réunion|dispo|disponible)', message, re.I)),
            'has_personalization': bool(re.search(r'(votre|votre|vos)', message, re.I)),
            'has_urgency': bool(re.search(r'(rapide|urgent|prochaine|semaine)', message, re.I)),
            'has_proof': bool(re.search(r'(%|€|\$|client|success)', message, re.I)),
            'tone_score': 0,
        }
        
        # Score de qualité
        quality_score = 0
        if analysis['length'] > 100:
            quality_score += 20
        if analysis['has_cta']:
            quality_score += 25
        if analysis['has_personalization']:
            quality_score += 20
        if analysis['has_urgency']:
            quality_score += 15
        if analysis['has_proof']:
            quality_score += 20
        
        analysis['quality_score'] = quality_score
        
        return analysis

# Instance globale
message_engine = MessageEngine()

__all__ = ['message_engine', 'MessageEngine']
"@

$content | Out-File -FilePath "src\modules\message_engine.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\modules\message_engine.py" -ForegroundColor Green