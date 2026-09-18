"""
PLANIFICATEUR DE CADENCE COMMERCIALE STRATÉGIQUE (MULTI-TOUCH CADENCE)
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any

class CadenceEngine:
    """Calcule le calendrier idéal d'une séquence de cold outreach sans week-end"""

    @staticmethod
    def add_business_days(start_date: datetime, business_days_to_add: int) -> datetime:
        """Ajoute des jours ouvrés en ignorant automatiquement les samedis et dimanches"""
        current_date = start_date
        added = 0
        while added < business_days_to_add:
            current_date += timedelta(days=1)
            # 0=Lundi, ..., 4=Vendredi, 5=Samedi, 6=Dimanche
            if current_date.weekday() < 5:
                added += 1
        return current_date

    def generate_timeline(self, start_date: datetime = None) -> List[Dict[str, Any]]:
        """Génère la cadence type 4 étapes (Email + Relances + Multi-canal)"""
        start = start_date or datetime.now()
        
        # J+0 : 09h15 (Heure d'or)
        step1_date = self.add_business_days(start, 0).replace(hour=9, minute=15, second=0)
        # J+3 ouvrés : 14h30
        step2_date = self.add_business_days(step1_date, 3).replace(hour=14, minute=30, second=0)
        # J+7 ouvrés : 10h00
        step3_date = self.add_business_days(step1_date, 7).replace(hour=10, minute=0, second=0)
        # J+12 ouvrés : 11h45
        step4_date = self.add_business_days(step1_date, 12).replace(hour=11, minute=45, second=0)

        return [
            {
                "step": 1,
                "type": "Cold Email (Accroche principale)",
                "scheduled_date": step1_date.strftime("%A %d %B à %Hh%M"),
                "goal": "Validation du problème & Déclenchement de l'intérêt"
            },
            {
                "step": 2,
                "type": "Bump Doux (Email) + Invitation LinkedIn",
                "scheduled_date": step2_date.strftime("%A %d %B à %Hh%M"),
                "goal": "Rappel de présence non-intrusif (< 40 mots)"
            },
            {
                "step": 3,
                "type": "Preuve Sociale & Cas Client (Email)",
                "scheduled_date": step3_date.strftime("%A %d %B à %Hh%M"),
                "goal": "Démonstration chiffrée de ROI pour vaincre le doute"
            },
            {
                "step": 4,
                "type": "Break-up Email Courtois (Clôture)",
                "scheduled_date": step4_date.strftime("%A %d %B à %Hh%M"),
                "goal": "FOMO & Retrait de la table pour susciter la réponse de dernière minute"
            }
        ]

cadence_engine = CadenceEngine()
