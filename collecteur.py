import time
import requests
import os
from datetime import datetime

# Configuration locale (Synchronisée au singulier)
LOG_FILE_PATH = r"C:\ProgramData\ssh\logs\sshd.log"
API_URL = "http://127.0.0.1:8000/api/v1/logs/ingest/raw"
HEARTBEAT_URL = "http://127.0.0.1:8000/api/v1/agent/heartbeat"

# Couleurs ANSI
C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_CYAN = "\033[96m"
C_END = "\033[0m"
C_BOLD = "\033[1m"

def get_time():
    return f"{C_BLUE}[{datetime.now().strftime('%H:%M:%S')}]{C_END}"

def send_heartbeat():
    try:
        payload = {"agent_id": "AGENT-WIN-SSHD-01", "hostname": "Windows-Server-Target", "status": "online"}
        requests.post(HEARTBEAT_URL, json=payload, timeout=2)
        print(f"{get_time()} {C_GREEN}{C_BOLD}[HEARTBEAT]{C_END} Signal de vie與Manager synchronisé.")
    except Exception:
        print(f"{get_time()} {C_YELLOW}{C_BOLD}[HEARTBEAT]{C_END} Serveur SIEM injoignable.")

# ─────────────────────────────────────────────────────────────────────────────
# BANNIÈRE D'ACCUEIL
# ─────────────────────────────────────────────────────────────────────────────
print(f"{C_CYAN}{C_BOLD}" + "=" * 65 + f"{C_END}")
print(f"{C_CYAN}{C_BOLD} 🛡️   SMART SIEM — AGENT DE COLLECTE WINDOWS (CIBLE){C_END}")
print(f"{C_CYAN}{C_BOLD}" + "=" * 65 + f"{C_END}")
print(f" {C_BOLD}[*]{C_END} Target Logfile : {C_YELLOW}{LOG_FILE_PATH}{C_END}")
print(f" {C_BOLD}[*]{C_END} SIEM Endpoint  : {C_YELLOW}{API_URL}{C_END}")
print(f"{C_CYAN}" + "─" * 65 + f"{C_END}")

# Création du fichier de simulation s'il manque
if not os.path.exists(LOG_FILE_PATH):
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    with open(LOG_FILE_PATH, "w") as tmp: pass
    print(f"{get_time()} {C_GREEN}{C_BOLD}[CREATION]{C_END} Fichier de simulation généré.")

print(f"{get_time()} {C_GREEN}{C_BOLD}[READY]{C_END} Écoute active lancée...\n")

# Premier signal au démarrage
send_heartbeat()

def tail_and_send():
    with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        last_heartbeat = time.time()
        
        while True:
            # Heartbeat toutes les 30 secondes
            if time.time() - last_heartbeat > 30:
                send_heartbeat()
                last_heartbeat = time.time()

            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            
            clean_line = line.strip()
            if clean_line:
                print(f"{get_time()} {C_BOLD}[DETECTED]{C_END} {clean_line[:65]}...")
                try:
                    headers = {"Content-Type": "text/plain"}
                    response = requests.post(API_URL, data=clean_line.encode('utf-8'), headers=headers)
                    if response.status_code in [200, 201]:
                        print(f"        └──> {C_GREEN}{C_BOLD}[SUCCESS]{C_END} Transmis à l'index SIEM (HTTP {response.status_code})")
                    else:
                        print(f"        └──> {C_RED}{C_BOLD}[REFUSED]{C_END} Code d'erreur (HTTP {response.status_code})")
                except Exception as e:
                    print(f"        └──> {C_RED}{C_BOLD}[FAILURE]{C_END} Connexion impossible : {str(e)}")

if __name__ == "__main__":
    try:
        tail_and_send()
    except KeyboardInterrupt:
        print(f"\n{get_time()} {C_YELLOW}{C_BOLD}[SHUTDOWN]{C_END} Arrêt propre de l'agent.")