"""
base.py
--------

Classe de base abstraite de tous les collecteurs Smart-SIEM.

Elle fournit uniquement les propriétés communes
aux collecteurs Linux et Windows.

Les classes filles doivent implémenter:
- La gestion de l'état (OS-spécifique)
- La collecte des journaux (OS-spécifique)
"""

import socket
from abc import ABC, abstractmethod
from typing import Generator, Dict

from agent.config_loader import ConfigLoader
from agent.logger import AgentLogger


class BaseCollector(ABC):
    """Classe abstraite de base pour tous les collecteurs."""

    def __init__(self,
                 config: ConfigLoader,
                 logger: AgentLogger):
        """Initialise les proprietes communes a tous les collecteurs."""
        self.config = config
        self.logger = logger.get_logger()
        self.hostname = socket.gethostname()
        self.perimetre_id = self.config.get(
            "agent",
            "perimetre_id",
            default="perimetre-dmz"
        )

    @abstractmethod
    def collect(self) -> Generator[Dict, None, None]:
        """Methode abstraite que chaque collecteur (Linux/Windows) doit implementer.
        
        Doit retourner un generateur de dictionnaires avec au minimum:
        - raw_line: le contenu brut du log
        - source: d'ou provient le log
        - os: le systeme d'exploitation
        """
        pass

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