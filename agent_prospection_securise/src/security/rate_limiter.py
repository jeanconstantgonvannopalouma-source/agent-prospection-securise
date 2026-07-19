$content = @"
"""
Module de Rate Limiting robuste
Protège l'application contre les abus et surcharges
"""

import time
import logging
from collections import defaultdict
from threading import Lock, RLock
from typing import Tuple, Dict, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate Limiter robuste et thread-safe
    Utilise sliding window algorithm
    """
    
    def __init__(self):
        """Initialise le rate limiter"""
        self.requests = defaultdict(list)
        self.lock = RLock()  # Recursive Lock pour thread-safety
        self.limit_per_minute = config.RATE_LIMIT_PER_MINUTE
        self.limit_per_hour = config.RATE_LIMIT_PER_HOUR
        
        # Stats
        self.total_rejected = 0
        self.total_allowed = 0
        
        logger.info(f"✓ Rate Limiter initialisé - {self.limit_per_minute}/min, {self.limit_per_hour}/h")
    
    def is_allowed(self, identifier: str, weight: int = 1) -> Tuple[bool, str]:
        """
        Vérifie si une requête est autorisée
        Utilise sliding window (plus précis que token bucket)
        
        Args:
            identifier: Identifiant unique (IP, user_id, email, etc.)
            weight: Poids de la requête (par défaut: 1)
            
        Returns:
            (is_allowed: bool, message: str)
        """
        if not identifier or not isinstance(identifier, str):
            logger.warning(f"❌ Identifiant invalide: {identifier}")
            return False, "Identifiant invalide"
        
        # Limite longueur identifiant
        identifier = identifier[:255]
        
        with self.lock:
            current_time = time.time()
            
            # ===== NETTOIE LES ANCIENNES REQUÊTES =====
            one_hour_ago = current_time - 3600
            one_minute_ago = current_time - 60
            
            # Garde seulement les requêtes de la dernière heure
            self.requests[identifier] = [
                (req_time, req_weight) for req_time, req_weight in self.requests[identifier]
                if req_time > one_hour_ago
            ]
            
            # ===== COMPTE LES REQUÊTES RÉCENTES =====
            requests_last_minute = sum(
                req_weight for req_time, req_weight in self.requests[identifier]
                if req_time > one_minute_ago
            )
            
            requests_last_hour = sum(
                req_weight for req_time, req_weight in self.requests[identifier]
            )
            
            # ===== VÉRIFIE LES LIMITES =====
            if requests_last_minute + weight > self.limit_per_minute:
                self.total_rejected += 1
                logger.warning(
                    f"⚠️ Rate limit MINUTE dépassé: {identifier} "
                    f"({requests_last_minute}/{self.limit_per_minute})"
                )
                remaining = max(0, 60 - (current_time - self.requests[identifier][0][0]))
                return False, f"Limite par minute dépassée. Réessayez dans {int(remaining)}s."
            
            if requests_last_hour + weight > self.limit_per_hour:
                self.total_rejected += 1
                logger.warning(
                    f"⚠️ Rate limit HEURE dépassé: {identifier} "
                    f"({requests_last_hour}/{self.limit_per_hour})"
                )
                remaining = max(0, 3600 - (current_time - self.requests[identifier][0][0]))
                return False, f"Limite par heure dépassée. Réessayez dans {int(remaining // 60)}min."
            
            # ===== AJOUTE LA REQUÊTE ACTUELLE =====
            self.requests[identifier].append((current_time, weight))
            self.total_allowed += 1
            
            logger.debug(
                f"✓ Requête autorisée: {identifier} "
                f"({requests_last_minute + weight}/{self.limit_per_minute} min)"
            )
            
            return True, "Autorisé"
    
    def get_stats(self, identifier: str) -> Dict[str, any]:
        """
        Retourne les statistiques d'utilisation pour un identifiant
        
        Args:
            identifier: Identifiant unique
            
        Returns:
            Dictionnaire des statistiques
        """
        with self.lock:
            current_time = time.time()
            
            requests_minute = sum(
                req_weight for req_time, req_weight in self.requests.get(identifier, [])
                if current_time - req_time < 60
            )
            
            requests_hour = sum(
                req_weight for req_time, req_weight in self.requests.get(identifier, [])
                if current_time - req_time < 3600
            )
            
            return {
                'identifier': identifier,
                'requests_per_minute': requests_minute,
                'limit_per_minute': self.limit_per_minute,
                'remaining_per_minute': max(0, self.limit_per_minute - requests_minute),
                'requests_per_hour': requests_hour,
                'limit_per_hour': self.limit_per_hour,
                'remaining_per_hour': max(0, self.limit_per_hour - requests_hour),
                'percentage_used_hour': round((requests_hour / self.limit_per_hour) * 100, 2),
                'is_throttled': requests_minute >= self.limit_per_minute,
            }
    
    def reset(self, identifier: Optional[str] = None) -> None:
        """
        Réinitialise les limites
        
        Args:
            identifier: Identifiant spécifique (None = réinitialiser tout)
        """
        with self.lock:
            if identifier:
                if identifier in self.requests:
                    del self.requests[identifier]
                    logger.info(f"✓ Rate limit réinitialisé: {identifier}")
            else:
                self.requests.clear()
                logger.info("✓ Tous les rate limits réinitialisés")
    
    def get_global_stats(self) -> Dict[str, any]:
        """Retourne les statistiques globales"""
        total_requests = self.total_allowed + self.total_rejected
        rejection_rate = 0
        if total_requests > 0:
            rejection_rate = round((self.total_rejected / total_requests) * 100, 2)
        
        return {
            'total_requests': total_requests,
            'total_allowed': self.total_allowed,
            'total_rejected': self.total_rejected,
            'rejection_rate_percent': rejection_rate,
            'active_identifiers': len(self.requests),
            'limit_per_minute': self.limit_per_minute,
            'limit_per_hour': self.limit_per_hour,
        }

# Instance globale
rate_limiter = RateLimiter()

__all__ = ['rate_limiter', 'RateLimiter']
"@

$content | Out-File -FilePath "src\security\rate_limiter.py" -Encoding UTF8 -NoNewline
Write-Host "✓ Fichier créé: src\security\rate_limiter.py" -ForegroundColor Green