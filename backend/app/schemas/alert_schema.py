from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AlertBaseSchema(BaseModel):
    id: str = Field(..., description="Identifiant unique de l'alerte générée.")
    timestamp: datetime = Field(..., description="Date et heure exactes de la levée de l'alerte.")
    niveau_criticite: str = Field(..., description="Niveau d'impact : 'INFO', 'WARNING', 'HIGH', 'CRITICAL'.")
    statut: str = Field(..., description="Cycle de vie : 'ouvert', 'en cours', 'résolu'.")
    regle_id: str = Field(..., description="Référence vers la règle de corrélation déclencheuse.")
    # Optionnel car au début, aucun analyste n'est encore assigné au ticket
    utilisateur_id: Optional[str] = Field(None, description="Analyste du SOC assigné au traitement.")

    class Config:
        from_attributes = True