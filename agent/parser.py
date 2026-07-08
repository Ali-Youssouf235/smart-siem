import socket

class LogParser:
    """Formate et normalise les logs bruts selon le modèle attendu par l'API"""

    def __init__(self, config):
        self.config = config
        self.hostname = socket.gethostname()
        self.perimetre_id = self.config.get("agent", "perimetre_id", default="perimetre-dmz")

    def parse(self, raw_data: dict) -> dict:
        """Transforme la ligne brute en objet conforme au contrat SIEM"""
        raw_line = raw_data.get("raw_line", "").strip()
        
        if not raw_line:
            return {}

        # CONTRAT STRICT DE L'API REST
        payload = {
            "raw_message": raw_line,
            "host": self.hostname,
            "perimetre_id": self.perimetre_id
        }

        return payload