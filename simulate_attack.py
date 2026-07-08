import time
import os
import sys

# Chemins standards des logs sur Linux
AUTH_LOG = "/var/log/auth.log"
SYS_LOG = "/var/log/syslog"

def generate_fake_attack(target_file):
    if not os.path.exists(target_file):
        print(f"[❌] Le fichier {target_file} n'existe pas. Tentative de création...")
        try:
            open(target_file, 'a').close()
        except PermissionError:
            print("[⚠️] Permission insuffisante. Lancez le script avec 'sudo'.")
            sys.exit(1)

    print(f"🚀 Début de la simulation d'attaque par force brute sur {target_file}...")
    print("Regardez le terminal de votre agent SIEM ou l'API de Rohan ! \n")

    # Liste de faux utilisateurs pour la force brute
    fake_users = ["root", "admin", "ubnt", "database", "rohan", "testuser"]

    try:
        for user in fake_users:
            timestamp = time.strftime("%b %d %H:%M:%S")
            # Message formaté simulant exactement une attaque SSH interceptée par l'OS
            log_entry = f"{timestamp} ubuntu-server sshd[9999]: Failed password for {user} from 192.168.43.20 port 49213 ssh2\n"
            
            with open(target_file, "a") as f:
                f.write(log_entry)
            
            print(f"[🔥 ATTAQUE] Injection : Tentative infructueuse avec l'utilisateur '{user}'")
            time.sleep(1.5) # Délai pour voir l'envoi en temps réel

        # Injection d'une commande sudo suspecte
        timestamp = time.strftime("%b %d %H:%M:%S")
        sudo_entry = f"{timestamp} ubuntu-server sudo:    hacker : TTY=pts/1 ; PWD=/root ; USER=root ; COMMAND=/usr/bin/apt-get remove ufw\n"
        with open(target_file, "a") as f:
            f.write(sudo_entry)
        print("[💀 CRITIQUE] Injection : Commande sudo malveillante (désactivation pare-feu).")

        print("\n✅ Simulation terminée avec succès.")

    except PermissionError:
        print("[❌] Erreur : Vous devez exécuter ce script avec 'sudo' pour écrire dans les logs système.")

if __name__ == "__main__":
    # Si auth.log est protégé, on peut tester sur syslog ou s'assurer d'être en sudo
    chosen_file = AUTH_LOG if os.path.exists(AUTH_LOG) else SYS_LOG
    generate_fake_attack(chosen_file)