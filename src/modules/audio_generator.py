"""
GÉNÉRATEUR AUDIO MP3 RÉEL POUR MESSAGES VOCAUX (TEXT-TO-SPEECH)
"""
import os
import time
import urllib.request
import urllib.parse
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RealAudioGenerator:
    """Transforme les textes de notes vocales en vrais fichiers audio MP3"""

    def generate_mp3(self, text_script: str) -> Dict[str, Any]:
        os.makedirs("data/audio", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"voice_note_{timestamp}.mp3"
        filepath = os.path.join("data", "audio", filename)

        # Troncature propre pour un message vocal fluide de 30-45s
        clean_text = text_script.replace("*", "").replace("---", "").strip()[:250]
        
        try:
            # Synthèse vocale via endpoint audio haute définition
            encoded_text = urllib.parse.quote(clean_text)
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=fr&client=tw-ob"
            
            req = urllib.request.Request(tts_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as response:
                audio_data = response.read()
                with open(filepath, "wb") as f:
                    f.write(audio_data)

            return {
                "success": True,
                "filename": filename,
                "audio_url": f"/data/audio/{filename}",
                "script_used": clean_text
            }
        except Exception as e:
            logger.error(f"Erreur génération audio MP3: {e}")
            return {
                "success": False,
                "error": str(e),
                "script_used": clean_text
            }

audio_generator = RealAudioGenerator()
