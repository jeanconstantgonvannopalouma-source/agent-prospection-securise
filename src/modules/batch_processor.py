"""
MOTEUR DE TRAITEMENT PAR LOT (BATCH PROCESSOR)
"""
import csv
import os
import time
import logging
from typing import List, Dict, Any
from core.agent import agent

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Traite des listes de leads CSV en série avec rapport d'export"""

    def process_csv_file(self, input_csv_path: str, value_prop: str = "Automatisation B2B") -> str:
        if not os.path.exists(input_csv_path):
            raise FileNotFoundError(f"Fichier introuvable : {input_csv_path}")

        leads = []
        with open(input_csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                leads.append(row)

        print(f"\n📂 {len(leads)} prospects chargés depuis '{input_csv_path}'.")
        print("⚡ Début du traitement IA par lot...")

        results = []
        for idx, lead in enumerate(leads, 1):
            name = lead.get('first_name') or lead.get('name') or 'Prospect'
            company = lead.get('company') or lead.get('company_name') or 'Entreprise'
            print(f"  [{idx}/{len(leads)}] Traitement de {name} ({company})...")

            res = agent.process_prospect(lead, value_prop=value_prop, auto_send=True)
            
            p_enriched = res["prospect"]
            msg = res["campaign_message"]
            qa = res["deliverability_analysis"]
            status = res["send_status"]

            results.append({
                "first_name": p_enriched.get("first_name", ""),
                "last_name": lead.get("last_name", ""),
                "email": lead.get("email", ""),
                "company": p_enriched.get("company", ""),
                "position": p_enriched.get("position", ""),
                "icp_score": p_enriched.get("qualification_score", 0),
                "ai_pain_point": p_enriched.get("top_pain_point", ""),
                "generated_subject": msg.get("subject", ""),
                "generated_body": msg.get("body", ""),
                "quality_score": msg.get("quality_score", 0),
                "deliverability_score": qa.get("deliverability_score", 100),
                "send_mode": status.get("mode", ""),
                "send_success": status.get("success", False)
            })
            time.sleep(0.5)  # Throttle pour fluidité

        # Export des résultats
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"rapport_campagne_{timestamp}.csv"
        
        fieldnames = list(results[0].keys()) if results else []
        with open(output_file, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        return output_file

batch_processor = BatchProcessor()
