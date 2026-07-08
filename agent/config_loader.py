"""
config_loader.py
----------------

Charge le fichier de configuration YAML de l'agent.
"""

import os
import yaml


class ConfigLoader:
    """Charge et fournit l'accès à la configuration."""

    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path
        self.config = self.load()

    def load(self):
        """Charge le fichier YAML."""

        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Fichier de configuration introuvable : {self.config_path}"
            )

        with open(self.config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def get(self, *keys, default=None):
        """
        Permet d'accéder facilement à une valeur.

        Exemple :
        config.get("backend", "url")
        """

        value = self.config

        for key in keys:

            if isinstance(value, dict):

                value = value.get(key)

            else:
                return default

        return value if value is not None else default