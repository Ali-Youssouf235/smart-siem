import socket
from .models import LogPayload


class LogParser:
    """Formate et normalise les logs bruts selon le modele attendu par l'API."""

    def __init__(self, config):
        self.config = config
        self.hostname = socket.gethostname()
        self.perimetre_id = self.config.get("agent", "perimetre_id", default="perimetre-dmz")

    def parse(self, raw_data: dict) -> dict:
        """Transforme la ligne brute en objet conforme au contrat SIEM.
        
        Retourne un dictionnaire pret a etre envoye a l'API backend.
        """
        raw_line = raw_data.get("raw_line", "").strip()
        
        if not raw_line:
            return {}

        # Creation d'une LogPayload validee
        payload_obj = LogPayload(
            raw_message=raw_line,
            host=self.hostname,
            perimetre_id=self.perimetre_id,
            meta_source=raw_data.get("source"),
            meta_os=raw_data.get("os")
        )
        
        # Validation et retour du contrat strict API
        if payload_obj.validate():
            return payload_obj.to_api_dict()
        
        return {}