"""
DÉMON AUTONOME D'ARRIÈRE-PLAN (BACKGROUND AUTOPILOT DAEMON)
"""
import time
import threading
import logging
from typing import Dict, Any
from modules.pipeline_tracker import pipeline_tracker
from modules.warmup_engine import warmup_engine
from core.agent import agent

logger = logging.getLogger(__name__)

class AutopilotDaemon:
    """Agent d'exécution autonome en tâche de fond"""

    def __init__(self):
        self.is_running = False
        self._thread = None
        self.processed_count = 0

    def _worker_loop(self, batch_size: int = 5):
        logger.info("🤖 Démon Autonome activé en arrière-plan.")
        while self.is_running:
            stats = pipeline_tracker.get_stats()
            recent = stats.get("recent_prospects", [])
            
            # Recherche de prospects à traiter (statut NOUVEAU)
            for p in recent:
                if not self.is_running:
                    break
                if p.get("status") == "NOUVEAU":
                    # Traitement IA
                    _ = agent.process_prospect(p, auto_send=True)
                    pipeline_tracker.update_status(p.get("email"), "CONTACTÉ")
                    self.processed_count += 1
                    warmup_engine.apply_human_jitter(simulation_mode=True)

            # Pause avant le prochain cycle de scrutation
            time.sleep(10)

    def start(self):
        """Démarre le démon en tâche de fond"""
        if not self.is_running:
            self.is_running = True
            self._thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._thread.start()

    def stop(self):
        """Arrête le démon"""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2)

autopilot_daemon = AutopilotDaemon()
