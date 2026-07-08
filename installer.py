import sys
import os
import platform
import tkinter as tk
from tkinter import simpledialog, messagebox
import yaml
import subprocess

def check_admin_privileges():
    """Verifie si l'utilisateur a les privileges administrateur."""
    system = platform.system()
    
    if system == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell.IsUserAnAdmin()
        except Exception:
            return False
    elif system == "Linux":
        return os.geteuid() == 0
    elif system == "Darwin":  # macOS
        return os.geteuid() == 0
    
    return False

def request_admin_password(root):
    """Demande le mot de passe administrateur a l'utilisateur."""
    system = platform.system()
    
    if system == "Windows":
        messagebox.showwarning(
            "Privileges Admin Requis",
            "L'agent SIEM necessite les privileges administrateur pour acceder aux logs Windows.\n\n"
            "Veuillez relancer ce programme en tant qu'administrateur.\n"
            "Faites un clic-droit sur le script et selectionnez 'Executer en tant qu'administrateur'."
        )
        return False
    
    elif system == "Linux":
        # Pour Linux, on demande le mot de passe via la GUI
        password = simpledialog.askstring(
            "Authentification Requise",
            "L'agent SIEM necessite les privileges root pour acceder aux logs (/var/log/).\n\n"
            "Entrez votre mot de passe:",
            show="*"
        )
        return password if password else None
    
    return None

def verify_linux_password(password):
    """Verifie le mot de passe Linux sans exposer sudo directement."""
    try:
        # Test: essaie d'executer une commande inoffensive avec sudo
        result = subprocess.run(
            ["sudo", "-S", "true"],
            input=password.encode() + b"\n",
            capture_output=True,
            timeout=5,
            text=False
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False

def create_config_file(api_url: str, system_type: str = "linux"):
    """Cree le fichier de configuration YAML selon l'OS."""
    
    # Configuration specifique a l'OS
    if system_type.lower() == "windows":
        log_files = [
            "Security",  # Event Log Windows
            "System"
        ]
        # Note: Windows utilisera wevtutil, pas des fichiers physiques
        logs_config = {
            "files": log_files,
            "source": "Windows Event Logs"
        }
    else:  # Linux
        log_files = [
            "/var/log/syslog",
            "/var/log/auth.log"
        ]
        logs_config = {
            "files": log_files,
            "source": "Linux System Logs"
        }
    
    config_data = {
        "agent": {
            "name": "Smart-SIEM-Agent",
            "version": "1.0.0",
            "buffer_max_size": 5000,
            "auto_start": True,
            "perimetre_id": "perimetre-dmz"
        },
        "backend": {
            "url": f"{api_url}/api/logs/ingest" if not api_url.endswith('/api/logs/ingest') else api_url,
            "timeout": 10,
            "retry_interval": 5
        },
        "logs": logs_config,
        "logging": {
            "level": "INFO",
            "file": "logs/agent.log"
        }
    }
    
    os.makedirs("config", exist_ok=True)
    with open("config/config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    print(f"[✓] Configuration sauvegardee avec l'API : {api_url}")
    print(f"[✓] Systeme detecte : {system_type.upper()}")

class InstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart SIEM Agent - Installation")
        self.root.geometry("550x420")
        self.root.resizable(False, False)
        
        self.api_url = tk.StringVar(value="http://")
        self.config_created = False
        self.linux_password = None
        self.system = platform.system()
        
        # Verification des privileges au demarrage
        if not self.check_privileges():
            self.root.destroy()
            return
        
        self.create_widgets()
    
    def check_privileges(self):
        """Verifie les privileges et demande auth si necessaire."""
        if self.system == "Linux" and not check_admin_privileges():
            # Demander le mot de passe
            self.linux_password = request_admin_password(self.root)
            if self.linux_password is None:
                messagebox.showerror("Erreur", "Installation annulee : mot de passe requis.")
                return False
            
            # Verifier le mot de passe
            if not verify_linux_password(self.linux_password):
                messagebox.showerror("Erreur", "Mot de passe incorrect. Installation annulee.")
                return False
            
            messagebox.showinfo("Succes", "Authentification reussie !")
        
        elif self.system == "Windows" and not check_admin_privileges():
            # Sur Windows, demander de relancer en admin
            request_admin_password(self.root)
            return False
        
        return True
    
    def create_widgets(self):
        tk.Label(self.root, text="Smart SIEM Agent", font=("Arial", 18, "bold")).pack(pady=15)
        tk.Label(self.root, text="Installation sur cette machine", font=("Arial", 12)).pack(pady=5)
        
        tk.Label(self.root, text="Adresse du Backend API :", font=("Arial", 10)).pack(anchor="w", padx=40, pady=(20,5))
        tk.Entry(self.root, textvariable=self.api_url, width=50, font=("Arial", 11)).pack(pady=5, padx=40)
        tk.Label(self.root, text="Exemple : http://10.237.69.157:8000", fg="gray").pack(pady=5)
        
        # Bouton 1 : Sauvegarde
        tk.Button(self.root, text="1️⃣ Sauvegarder la Configuration", font=("Arial", 10, "bold"),
                  bg="#17a2b8", fg="white", height=2, width=40,
                  command=self.save_config).pack(pady=15)
        
        # Bouton 2 : Lancement en arrière-plan
        self.install_btn = tk.Button(self.root, text="2️⃣ Installer et Démarrer l'Agent", 
                                    font=("Arial", 11, "bold"), bg="#28a745", fg="white", 
                                    height=2, width=40, state="disabled", command=self.start_agent_background)
        self.install_btn.pack(pady=10)
        
        tk.Label(self.root, text="L'installation créera les dossiers nécessaires\net démarrera l'agent en arrière-plan.", 
                 fg="gray", justify="center").pack(pady=20)
    
    def save_config(self):
        url = self.api_url.get().strip()
        if not url or url == "http://":
            messagebox.showerror("Erreur", "Veuillez entrer une adresse valide")
            return
        
        if not url.startswith("http"):
            url = "http://" + url
        
        create_config_file(url, self.system)
        messagebox.showinfo("Succes", "Configuration sauvegardee avec succes !")
        self.config_created = True
        self.install_btn.config(state="normal")
    
    def start_agent_background(self):
        """Lance main.py en tache de fond selon l'OS avec authentification."""
        try:
            if self.system == "Linux":
                # Sur Linux: utiliser sudo avec le mot de passe stocke
                if self.linux_password:
                    # Lancer main.py avec sudo en arriere-plan
                    cmd = "nohup sudo python3 main.py > agent_start.log 2>&1 &"
                    # Passer le mot de passe via pipe
                    process = subprocess.Popen(
                        cmd,
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    process.communicate(input=self.linux_password + "\n", timeout=5)
                else:
                    # Fallback: juste tenter le lancement
                    os.system("nohup sudo python3 main.py > agent_start.log 2>&1 &")
            
            elif self.system == "Windows":
                # Sur Windows: lancer avec le contexte admin actuel
                # PowerShell pour executer en arriere-plan
                ps_cmd = (
                    "Start-Process python -ArgumentList 'main.py' "
                    "-WorkingDirectory '{}' -WindowStyle Hidden -NoNewWindow"
                ).format(os.getcwd())
                
                subprocess.Popen(
                    ["powershell.exe", "-Command", ps_cmd],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            
            elif self.system == "Darwin":  # macOS
                # Sur macOS: utiliser sudo comme sur Linux
                cmd = "nohup sudo python3 main.py > agent_start.log 2>&1 &"
                os.system(cmd)
            
            messagebox.showinfo(
                "Installation Reussie",
                "L'agent Smart-SIEM a ete deploye et s'execute desormais en arriere-plan !\n\n"
                "Les logs sont disponibles dans : agent_start.log"
            )
            self.root.destroy()
        
        except Exception as e:
            messagebox.showerror("Erreur d'installation", f"Impossible de lancer l'agent : {e}")

if __name__ == "__main__":
    gui = InstallerGUI()
    gui.root.mainloop()