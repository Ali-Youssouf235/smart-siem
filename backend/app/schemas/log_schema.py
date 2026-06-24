from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LogBaseSchema(BaseModel):
    # UUID v4 représenté sous forme de chaîne de caractères
    id: str = Field(..., description="Identifiant unique universel (UUID v4) de l'événement.")
    timestamp: datetime = Field(..., description="Date et heure de génération du log.")
    source_ip: str = Field(..., description="Adresse IP d'origine (IPv4/IPv6).")
    # Optionnel (Nullable dans le dictionnaire de données)
    destination_ip: Optional[str] = Field(None, description="Adresse IP de destination.")
    host: str = Field(..., description="Nom de la machine ou serveur émetteur.")
    log_type: str = Field(..., description="Catégorie : 'auth', 'réseau', 'système', 'application'.")
    severity: str = Field(..., description="Niveau de sévérité : 'info', 'warning', 'critical'.")
    raw_message: str = Field(..., description="Contenu textuel brut d'origine avant traitement.")
    is_suspect: bool = Field(default=False, description="Flag d'enquête pour l'analyste SOC.")
    perimetre_id: str = Field(..., description="Clé étrangère vers le périmètre de sécurité.")

    class Config:
        from_attributes = True