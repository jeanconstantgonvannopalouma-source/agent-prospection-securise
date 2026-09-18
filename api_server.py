"""
SERVEUR API HEADLESS POUR L'AGENT STRATOSPHÉRIQUE
Expose les fonctionnalités via des requêtes HTTP REST (Port 8000)
"""
import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.abspath("src"))

from core.agent import agent
from modules.pipeline_tracker import pipeline_tracker
from modules.reply_triage import reply_triage
from modules.web_researcher import web_researcher
from modules.tech_stack_spy import tech_stack_spy

class AgentAPIRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        if self.path == "/api/health":
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "healthy", "agent": "Stratospheric V9.0"}).encode("utf-8"))
        elif self.path == "/api/stats":
            self._set_headers(200)
            stats = pipeline_tracker.get_stats()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Route introuvable"}).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        payload = json.loads(body.decode('utf-8')) if body else {}

        if self.path == "/api/prospect":
            # Endpoint pour traiter un lead à la volée
            res = agent.process_prospect(payload, auto_send=False)
            self._set_headers(200)
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/triage":
            # Endpoint pour classifier une réponse reçue
            reply_text = payload.get("reply_text", "")
            res = reply_triage.analyze_reply(payload.get("prospect", {}), reply_text)
            self._set_headers(200)
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/tech-spy":
            # Endpoint pour espionner la stack d'un site web
            domain = payload.get("domain", "doctolib.fr")
            res = tech_stack_spy.generate_technographic_pitch(domain, domain, "IA B2B")
            self._set_headers(200)
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Route POST inconnue"}).encode("utf-8"))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, AgentAPIRequestHandler)
    print(f"\n🚀 SERVEUR API STRATOSPHÉRIQUE EN LIGNE SUR : http://localhost:{port}")
    print(f"📡 Endpoints actifs :")
    print(f"  • GET  http://localhost:{port}/api/health")
    print(f"  • GET  http://localhost:{port}/api/stats")
    print(f"  • POST http://localhost:{port}/api/prospect")
    print(f"  • POST http://localhost:{port}/api/triage")
    print(f"  • POST http://localhost:{port}/api/tech-spy")
    print("\nAppuie sur Ctrl+C pour stopper le serveur API.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Serveur API arrêté.")

if __name__ == "__main__":
    run_server()
