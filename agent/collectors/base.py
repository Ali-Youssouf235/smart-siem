"""
base.py
--------

Classe de base de tous les collecteurs Smart-SIEM.

Elle fournit toutes les fonctionnalités communes
aux collecteurs Linux et Windows.

Les classes filles n'ont qu'à implémenter
la collecte des journaux.
"""

import os
import glob
import json
import socket

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List

from agent.config_loader import ConfigLoader
from agent.logger import AgentLogger


from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent / "agent_state.json"

class BaseCollector(ABC):

    def __init__(self,
                 config: ConfigLoader,
                 logger: AgentLogger):

        self.config = config
        self.logger = logger.get_logger()

        self.hostname = socket.gethostname()

        self.perimetre_id = self.config.get(
            "agent",
            "perimetre_id",
            default="perimetre-dmz"
        )

        self.dev_mode = self.config.get(
            "agent",
            "dev_mode",
            default=True
        )

        self.file_positions = {}

        self._load_state()

    # ==========================================================
    # Gestion de l'état
    # ==========================================================

    def _load_state(self):

        if os.path.exists(STATE_FILE):

            try:

                with open(
                    STATE_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:

                    self.file_positions = json.load(f)

                self.logger.info("Etat précédent restauré.")

            except Exception as e:

                self.logger.warning(
                    f"Impossible de restaurer l'état : {e}"
                )

                self.file_positions = {}

    def _save_state(self):

        try:

            with open(
                STATE_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.file_positions,
                    f,
                    indent=4
                )

        except Exception as e:

            self.logger.error(
                f"Impossible de sauvegarder l'état : {e}"
            )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def _get_timestamp(self):

        return datetime.now(
            timezone.utc
        ).isoformat()

    def _resolve_log_files(self) -> List[str]:

        files = []

        patterns = self.config.get(
            "logs",
            "files",
            default=[]
        )

        for pattern in patterns:

            matched = glob.glob(
                pattern,
                recursive=True
            )

            if matched:

                files.extend(matched)

                self.logger.info(
                    f"{pattern} -> {len(matched)} fichier(s)"
                )

            else:

                self.logger.warning(
                    f"Aucun fichier trouvé : {pattern}"
                )

        return list(dict.fromkeys(files))

    # ==========================================================
    # Filtre sécurité
    # ==========================================================

    def _is_security_relevant(self,
                              line: str) -> bool:

        if not line:

            return False

        if self.dev_mode:

            return True

        keywords = self.config.get(
            "security",
            "keywords",
            default=[]
        )

        line = line.lower()

        return any(
            keyword.lower() in line
            for keyword in keywords
        )

    # ==========================================================
    # Type de log
    # ==========================================================

    def _guess_log_type(self,
                        filepath: str):

        fp = filepath.lower()

        if "security" in fp:
            return "security"

        if "application" in fp:
            return "application"

        if "system" in fp:
            return "system"

        if "auth" in fp:
            return "auth"

        if "secure" in fp:
            return "auth"

        if "syslog" in fp:
            return "syslog"

        if "kern" in fp:
            return "kernel"

        return "unknown"

    # ==========================================================
    # Méthode à implémenter
    # ==========================================================

    @abstractmethod
    def get_new_logs(self):
        """
        Cette méthode devra être implémentée
        par LinuxCollector et WindowsCollector.
        """
        pass