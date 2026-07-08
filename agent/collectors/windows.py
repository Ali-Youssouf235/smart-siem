import os
import subprocess
import json
from typing import Generator, Dict
from .base import BaseCollector


class WindowsLogCollector(BaseCollector):
    """Collecteur specifique pour les Event Logs Windows (Security, System)."""

    def __init__(self, config, logger):
        """Initialise le collecteur Windows avec gestion d'etat autonome."""
        super().__init__(config, logger)
        self.state_file = "agent_state_windows.json"
        self.file_positions = self._load_state()
        # Initialise l'index du dernier evenement lu si absent
        if "last_record_id" not in self.file_positions:
            self.file_positions["last_record_id"] = 0

    def _load_state(self) -> dict:
        """Restaure l'etat precedent des logs Windows lus."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Impossible de charger l'etat Windows : {e}")
        return {}

    def _save_state(self):
        """Sauvegarde l'etat des positions de lecture."""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.file_positions, f)
        except Exception as e:
            self.logger.error(f"Impossible de sauvegarder l'etat Windows : {e}")

    def collect(self) -> Generator[Dict, None, None]:
        """Execute une commande PowerShell/CMD pour extraire les logs de securite recents."""
        try:
            last_id = self.file_positions.get("last_record_id", 0)
            
            # Commande wevtutil pour obtenir les logs de securite au format texte
            # Filtre les evenements plus recents que le dernier record sauvegarde
            cmd = f'wevtutil qe Security /q:"Event[System[EventRecordID>{last_id}]]" /f:text /c:100'
            
            result = subprocess.run(["cmd.exe", "/c", cmd], capture_output=True, text=True, encoding="utf-8")
            
            if result.return_code == 0 and result.stdout.strip():
                # Decoupe les logs (chaque evenement est separe par des lignes vides)
                events = result.stdout.split("\n\n")
                
                for event in events:
                    if event.strip():
                        yield {
                            "raw_line": event.strip(),
                            "source": "Windows-Security-Log",
                            "os": "windows"
                        }
                
                # Mise a jour de l'etat (dans un environnement reel, parser l'EventRecordID)
                self._save_state()
            else:
                self.logger.debug("Aucun nouvel evenement Windows detecte.")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte Windows : {e}")