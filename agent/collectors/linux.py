import os
import glob
import json
from typing import Generator, Dict
from .base import BaseCollector


class LinuxLogCollector(BaseCollector):
    """Collecteur specifique pour les systemes Linux (Ubuntu, Debian, etc.)."""

    def __init__(self, config, logger):
        """Initialise le collecteur Linux avec gestion d'etat autonome."""
        super().__init__(config, logger)
        self.log_patterns = self.config.get("logs", "files", default=["/var/log/auth.log", "/var/log/syslog"])
        self.state_file = "agent_state_linux.json"
        self.file_positions = self._load_state()

    def _load_state(self) -> dict:
        """Restaure l'etat precedent des fichiers lus."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Impossible de charger l'etat Linux : {e}")
        return {}

    def _save_state(self):
        """Sauvegarde l'etat des positions de lecture."""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.file_positions, f)
        except Exception as e:
            self.logger.error(f"Impossible de sauvegarder l'etat Linux : {e}")

    def collect(self) -> Generator[Dict, None, None]:
        """Collecte les nouveaux logs depuis les fichiers Linux configures."""
        resolved_files = []
        for pattern in self.log_patterns:
            resolved_files.extend(glob.glob(pattern))

        state_changed = False

        for file_path in set(resolved_files):
            if not os.path.exists(file_path):
                continue

            try:
                current_size = os.path.getsize(file_path)
                
                # Premier lancement : on lit les 2000 derniers octets au lieu de tout ignorer
                if file_path not in self.file_positions:
                    self.file_positions[file_path] = max(0, current_size - 2000)
                    state_changed = True

                # Detection de rotation de logs
                if current_size < self.file_positions[file_path]:
                    self.logger.info(f"Rotation de logs detectee : {file_path}")
                    self.file_positions[file_path] = 0

                # Lecture des nouveaux logs
                if current_size > self.file_positions[file_path]:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(self.file_positions[file_path])
                        lines = f.readlines()
                        
                        for line in lines:
                            if line.strip():
                                yield {
                                    "raw_line": line.strip(),
                                    "source": file_path,
                                    "os": "linux"
                                }
                        
                    # Avance de la position
                    self.file_positions[file_path] = current_size
                    state_changed = True

            except Exception as e:
                self.logger.error(f"Erreur de lecture sur {file_path} : {e}")

        if state_changed:
            self._save_state()