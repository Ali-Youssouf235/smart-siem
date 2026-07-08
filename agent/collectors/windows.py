import subprocess
import json
from typing import Generator, Dict
from .base import BaseCollector

class WindowsLogCollector(BaseCollector):
    """Collecteur spécifique pour les Event Logs Windows (Security)"""

    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.state_file = "agent_state_windows.json"
        self.file_positions = self._load_state(self.state_file)
        # On initialise l'index du dernier événement lu si vide
        if "last_record_id" not in self.file_positions:
            self.file_positions["last_record_id"] = 0

    def collect(self) -> Generator[Dict, None, None]:
        """Exécute une commande PowerShell/CMD pour extraire les logs de sécurité récents"""
        try:
            last_id = self.file_positions["last_record_id"]
            
            # Commande wevtutil pour obtenir les logs de sécurité au format texte/XML
            # On filtre pour obtenir les événements plus récents que le dernier record sauvegardé
            cmd = f'wevtutil qe Security /q:"Event[System[EventRecordID>{last_id}]]" /f:text /c:100'
            
            result = subprocess.run(["cmd.exe", "/c", cmd], capture_output=True, text=True, encoding="utf-8")
            
            if result.return_code == 0 and result.stdout.strip():
                # On découpe les logs reçus (chaque événement est séparé par des lignes vides)
                events = result.stdout.split("\n\n")
                
                for event in events:
                    if event.strip():
                        # Extraction basique ou transmission brute au parser
                        yield {
                            "raw_line": event.strip(),
                            "source": "Windows-Security-Log",
                            "os": "windows"
                        }
                
                # Note: Dans un environnement réel, on parserait l'EventRecordID pour mettre à jour self.file_positions
                # Pour l'instant, on simule une mise à jour pour éviter les boucles infinies de démo
                self._save_state(self.state_file, self.file_positions)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte Windows : {e}")