"""Rate limiting robuste"""
import time
import logging
from collections import defaultdict
from threading import RLock

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, per_minute=60, per_hour=1000):
        self.requests = defaultdict(list)
        self.lock = RLock()
        self.limit_per_minute = per_minute
        self.limit_per_hour = per_hour
        self.total_rejected = 0
        self.total_allowed = 0
    
    def is_allowed(self, identifier: str, weight: int = 1) -> tuple:
        if not identifier or not isinstance(identifier, str):
            return False, "Identifiant invalide"
        
        identifier = identifier[:255]
        
        with self.lock:
            current_time = time.time()
            
            # Nettoie les anciennes requêtes
            self.requests[identifier] = [
                (req_time, req_weight) for req_time, req_weight in self.requests[identifier]
                if current_time - req_time < 3600
            ]
            
            # Compte
            requests_minute = sum(
                req_weight for req_time, req_weight in self.requests[identifier]
                if current_time - req_time < 60
            )
            
            requests_hour = sum(
                req_weight for req_time, req_weight in self.requests[identifier]
            )
            
            # Vérifie limites
            if requests_minute + weight > self.limit_per_minute:
                self.total_rejected += 1
                return False, "Limite minute dépassée"
            
            if requests_hour + weight > self.limit_per_hour:
                self.total_rejected += 1
                return False, "Limite heure dépassée"
            
            self.requests[identifier].append((current_time, weight))
            self.total_allowed += 1
            
            return True, "Autorisé"
    
    def get_stats(self, identifier: str) -> dict:
        current_time = time.time()
        
        requests_minute = sum(
            req_weight for req_time, req_weight in self.requests.get(identifier, [])
            if current_time - req_time < 60
        )
        
        requests_hour = sum(
            req_weight for req_time, req_weight in self.requests.get(identifier, [])
        )
        
        return {
            'requests_per_minute': requests_minute,
            'limit_per_minute': self.limit_per_minute,
            'requests_per_hour': requests_hour,
            'limit_per_hour': self.limit_per_hour,
        }

rate_limiter = RateLimiter()
