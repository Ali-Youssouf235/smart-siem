import time
import os
import sys

LOG_FILE_PATH = r"C:\ProgramData\ssh\logs\sshd.log"

print("[DEBUG] Étape 1 : Le script démarre...")

if not os.path.exists(LOG_FILE_PATH):
    print(f"[DEBUG] Étape 2 : Le fichier n'existe pas. Création...")
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
        f.write("--- Fichier de test initialisé ---\n")

print(f"[DEBUG] Étape 3 : Fichier présent. Tentative d'ouverture de {LOG_FILE_PATH}...")

try:
    # On ouvre en 'rb' (Binary Mode) pour éviter TOUT problème d'encodage Windows
    with open(LOG_FILE_PATH, "rb") as f:
        print("[DEBUG] Étape 4 : Fichier ouvert avec succès. Déplacement à la fin...")
        f.seek(0, os.SEEK_END)
        print("[🟢] AGENT ACTIF. En attente de logs... (Fais échouer un SSH maintenant)")
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            
            # Décodage propre de la ligne binaire
            try:
                clean_line = line.decode('utf-8').strip()
            except:
                clean_line = line.decode('cp1252', errors='ignore').strip()
                
            if clean_line:
                print(f"[👁️ AGENT CAPTURE] -> {clean_line}")
                sys.stdout.flush() # Force Windows à afficher la ligne immédiatement
                
except Exception as e:
    print(f"[🔴] CRASH DU SCRIPT : {str(e)}")