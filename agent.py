import time
import requests
import os

# Configuration de l'agent
API_URL = "http://127.0.0.1:8000/api/v1/logs/ingest/raw"
LOG_FILE_PATH = "auth.log"  # Le fichier que l'agent va surveiller

print("=" * 60)
print("              SMART SIEM — AGENT DE COLLECTE")
print("=" * 60)
print(f"[*] Surveillance du fichier : {LOG_FILE_PATH}")
print(f"[*] Envoi des flux vers     : {API_URL}")

# Création du fichier de log s'il n'existe pas pour éviter les erreurs
if not os.path.exists(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, "w") as f:
        f.write("")
    print("[+] Fichier auth.log créé à la racine.")

def tail_and_send():
    """Lit les nouvelles lignes du fichier et les envoie à l'API"""
    with open(LOG_FILE_PATH, "r") as f:
        # Aller directement à la fin du fichier pour ne lire que les nouveautés
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)  # Attendre 500ms avant de revérifier
                continue
                
            clean_line = line.strip()
            if clean_line:
                print(f"[->] Nouveau log détecté : {clean_line[:60]}...")
                try:
                    # Envoi au format text/plain comme attendu par FastAPI
                    headers = {"Content-Type": "text/plain"}
                    response = requests.post(API_URL, data=clean_line.encode('utf-8'), headers=headers)
                    
                    if response.status_code == 201:
                        print(f"    [🟢] Transmis avec succès ! (Code {response.status_code})")
                    else:
                        print(f"    [🔴] Erreur API : Code {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"    [❌] Impossible de joindre l'API : {str(e)}")

if __name__ == "__main__":
    try:
        tail_and_send()
    except KeyboardInterrupt:
        print("\n[*] Arrêt de l'agent SIEM. Fin de la collecte.")