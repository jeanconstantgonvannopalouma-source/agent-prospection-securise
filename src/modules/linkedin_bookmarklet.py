"""
BOOKMARKLET LINKEDIN 1-CLICK ET ANALYSEUR DE PROFIL SUR PAGE
"""
import os
import re
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LinkedInBookmarkletManager:
    """Gère l'analyse 1-click depuis LinkedIn et fournit le code Bookmarklet"""

    def get_bookmarklet_code(self, server_url: str = "http://localhost:5001") -> str:
        """Génère le script JS à glisser dans la barre de favoris Chrome"""
        js_code = f"""javascript:(function(){{
            var selText = window.getSelection().toString();
            var profileName = document.querySelector('h1') ? document.querySelector('h1').innerText.trim() : 'Prospect';
            var headline = document.querySelector('.text-body-medium') ? document.querySelector('.text-body-medium').innerText.trim() : '';
            var promptText = 'Prospecte ' + profileName + ' (' + headline + '). Note: ' + selText;
            
            fetch('{server_url}/api/chat', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{message: promptText}})
            }}).then(r=>r.json()).then(data=>{{
                alert('📧 MESSAGE GÉNÉRÉ PAR L\'AGENT :\\n\\n' + data.reply);
            }}).catch(e=>alert('Erreur de connexion avec l\'agent: ' + e));
        }})();"""
        return js_code.replace("\n", "").replace("  ", "")

linkedin_bookmarklet = LinkedInBookmarkletManager()
