"""
MOTEUR D'EXPORT MULTI-SÉQUENCES POUR SMARTLEAD / LEMLIST / INSTANTLY
"""
import csv
import json
import os
import logging
from typing import Dict, Any, List
from modules.message_engine import message_engine
from modules.voice_loom_generator import voice_loom_generator

logger = logging.getLogger(__name__)

class SequenceExporter:
    """Génère une campagne multi-touch 5 étapes et l'exporte au format universel"""

    def generate_full_sequence(self, prospect: Dict[str, Any], value_prop: str = "") -> Dict[str, Any]:
        p_name = prospect.get("first_name", "Prospect")
        p_company = prospect.get("company", "l'Entreprise")

        # Étape 1 : Cold Email Principal (PAS)
        e1 = message_engine.generate_personalized_message(prospect, value_prop=value_prop, framework="PAS")
        subject = e1.get("subject", f"Question pour {p_company}")

        # Étape 2 : Note d'invitation LinkedIn (< 280 car.)
        voice_data = voice_loom_generator.generate_voice_and_loom_script(prospect, value_prop)
        linkedin_note = voice_data.get("linkedin_voice_note_script", f"Bonjour {p_name}, ravi d'échanger sur l'actualité de {p_company} !")

        # Étape 3 : Relance Bump Doux (J+3)
        e2_body = f"Bonjour {p_name},\n\nJe me permets une brève relance suite à mon précédent message concernant {p_company}.\n\nEst-ce un sujet d'actualité pour vous ce trimestre ?\n\nBien à vous,"

        # Étape 4 : Preuve Sociale & Script Loom (J+7)
        loom_script = voice_data.get("loom_video_script", {})
        e3_body = f"Bonjour {p_name},\n\nJ'ai préparé une courte démo visuelle de 60s adaptée aux enjeux de {p_company}.\n\nSeriez-vous curieux d'y jeter un œil ?\n\nBien à vous,"

        # Étape 5 : Breakup Email (J+12)
        e4_body = f"Bonjour {p_name},\n\nSans retour de votre part, je conclue que le timing n'est pas opportun et je ferme votre dossier.\n\nBonne continuation dans vos projets chez {p_company},"

        sequence = {
            "prospect_email": prospect.get("email", ""),
            "first_name": p_name,
            "company": p_company,
            "step_1_email_subject": subject,
            "step_1_email_body": e1.get("body", ""),
            "step_2_linkedin_note": linkedin_note,
            "step_3_followup_email": e2_body,
            "step_4_loom_value_email": e3_body,
            "step_5_breakup_email": e4_body
        }
        return sequence

    def export_sequence_to_csv(self, sequence_data: Dict[str, Any], filename: str = "data/sequence_smartlead_export.csv") -> str:
        os.makedirs("data", exist_ok=True)
        fieldnames = list(sequence_data.keys())
        
        file_exists = os.path.exists(filename)
        with open(filename, mode='a' if file_exists else 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(sequence_data)
            
        return filename

sequence_exporter = SequenceExporter()
