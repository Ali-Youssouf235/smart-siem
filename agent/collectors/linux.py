import os
import glob
import json
from typing import Generator, Dict
from .base import BaseCollector

class LinuxLogCollector(BaseCollector):
    """Collecteur spécifique pour les systèmes Linux (Ubuntu)"""

    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.log_sys = logger.get_logger()
        self.log_patterns = self.config.get("logs", "linux_files", default=["/var/log/auth.log"])
        self.state_file = "agent_state_linux.json"
        self.file_positions = self._local_load_state()

    def _local_load_state(self) -> dict:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.log_sys.warning(f"Impossible de charger l'état : {e}")
        return {}

    def _local_save_state(self):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.file_positions, f)
        except Exception as e:
            self.log_sys.error(f"Impossible de sauvegarder l'état : {e}")

    def get_new_logs(self) -> Generator[Dict, None, None]:
        resolved_files = []
        for pattern in self.log_patterns:
            resolved_files.extend(glob.glob(pattern))

        state_changed = False

        for file_path in set(resolved_files):
            if not os.path.exists(file_path):
                continue

            try:
                current_size = os.path.getsize(file_path)
                
                # FORCE LE TEST : Si c'est le premier lancement, on lit les 2000 derniers octets au lieu de tout ignorer
                if file_path not in self.file_positions:
                    self.file_positions[file_path] = max(0, current_size - 2000)
                    state_changed = True

                if current_size < self.file_positions[file_path]:
                    self.log_sys.info(f"Rotation détectée : {file_path}")
                    self.file_positions[file_path] = 0

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
                        
                    self.file_positions[file_path] = current_size # <-- CORRIGÉ : On avance la position
                    state_changed = True

            except Exception as e:
                self.log_sys.error(f"Erreur de lecture sur {file_path} : {e}")

        if state_changed:
            self._local_save_state()

    def collect(self) -> Generator[Dict, None, None]:
        yield from self.get_new_logs()