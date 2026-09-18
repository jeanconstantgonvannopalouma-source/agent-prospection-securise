import json, sys
import urllib.request

url = "http://127.0.0.1:5001/api/chat"
session_id = "terminal_session"

print("==================================================")
print("   🤖 AGENT DE PROSPECTION — CHAT TERMINAL")
print("==================================================")
print("Tape tes messages ci-dessous.")
print("Tape 'exit' ou 'quit' pour quitter le chat.\n")

while True:
    try:
        msg = input("Vous > ").strip()
        if not msg:
            continue
        if msg.lower() in ["exit", "quit", "q"]:
            print("Fermeture du chat terminal. À bientôt !")
            break

        payload = json.dumps({"message": msg, "session_id": session_id}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            reply = res_data.get("reply") or res_data.get("error") or "Pas de réponse."
            engine = res_data.get("engine", "inconnu")
            model = res_data.get("model", "N/A")
            tools = res_data.get("tools_used", [])

            print(f"\nAgent [{engine} | {model}] >")
            print(f"{reply}\n")
            if tools:
                print(f"🛠️ [Outils exécutés : {tools}]\n")
            print("-" * 50)

    except KeyboardInterrupt:
        print("\nChat interrompu.")
        break
    except Exception as e:
        print(f"\n❌ [Erreur de connexion au serveur : {e}]")
        print("Vérifie que 'python .\\src\\main.py' tourne bien sur le port 5001.\n")