"""
WORKER D'ARRIÈRE-PLAN SÉCURISÉ (SAFE WORKER)
"""
import time
import logging

logger = logging.getLogger(__name__)

def run_worker():
    print("🤖 Worker arrière-plan actif et sécurisé.")
    while True:
        time.sleep(30)

if __name__ == "__main__":
    run_worker()
