from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class LogPayload:
    """Modèle de données strict validant le contrat de l'API de Rohan"""
    raw_message: str
    host: str
    perimetre_id: str
    
    # Métadonnées locales de diagnostic optionnelles (non envoyées à l'API si rejetées)
    meta_source: Optional[str] = None
    meta_os: Optional[str] = None

    def to_api_dict(self) -> dict:
        """Exclut les métadonnées internes pour envoyer uniquement le contrat exact exigé par l'API"""
        return {
            "raw_message": self.raw_message,
            "host": self.host,
            "perimetre_id": self.perimetre_id
        }

    def validate(self) -> bool:
        """Vérifie la conformité de l'objet avant expédition"""
        if not self.raw_message or not self.host or not self.perimetre_id:
            return False
        return True