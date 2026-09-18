"""
MOTEUR DE CHAUFFE (WARMUP) ET PROTECTION ANTI-BOT JITTER
"""
import random
import time
import logging

logger = logging.getLogger(__name__)

class WarmupEngine:
    """Régule les débits d'envois et simule un comportement humain naturel"""

    def __init__(self, account_age_days: int = 14):
        self.account_age_days = account_age_days

    def get_daily_safe_limit(self) -> int:
        """Calcule le volume max d'emails sécurisé par jour selon la maturité du domaine"""
        if self.account_age_days < 7:
            return 15  # Semaine 1 : Montée douce
        elif self.account_age_days < 14:
            return 35  # Semaine 2 : Vitesse intermédiaire
        elif self.account_age_days < 30:
            return 75  # Semaine 3-4 : Régime de croisière
        else:
            return 120 # Compte chaud : Pleine puissance

    def apply_human_jitter(self, min_seconds: int = 2, max_seconds: int = 5, simulation_mode: bool = True):
        """Injecte une pause aléatoire pour briser les patterns d'automatisation"""
        delay = random.uniform(min_seconds, max_seconds) if not simulation_mode else random.uniform(0.2, 0.6)
        time.sleep(delay)
        return delay

warmup_engine = WarmupEngine()
