from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any
import uuid

class LogBaseSchema(BaseModel):
    # 🟢 Si le parser ne génère pas d'ID, on crée un UUID v4 automatiquement
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        description="Identifiant unique universel (UUID v4) de l'événement."
    )
    
    # 🟢 Si le parser n'a pas extrait de date, on prend l'heure actuelle du serveur SIEM
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow, 
        description="Date et heure de génération du log."
    )
    
    # 🟢 IP Source : Devient optionnelle. Par défaut "127.0.0.1" (parfait pour les logs Windows locaux)
    source_ip: Optional[str] = Field(
        default="127.0.0.1", 
        description="Adresse IP d'origine (IPv4/IPv6)."
    )
    
    destination_ip: Optional[str] = Field(
        default=None, 
        description="Adresse IP de destination."
    )
    
    # 🟢 Tous les autres champs reçoivent une valeur par défaut pour ne jamais faire échouer l'ingestion
    host: Optional[str] = Field(
        default="localhost", 
        description="Nom de la machine ou serveur émetteur."
    )
    
    log_type: Optional[str] = Field(
        default="système", 
        description="Catégorie : 'auth', 'réseau', 'système', 'application'."
    )
    
    severity: Optional[str] = Field(
        default="info", 
        description="Niveau de sévérité : 'info', 'warning', 'critical'."
    )
    
    raw_message: Optional[str] = Field(
        default="", 
        description="Contenu textuel brut d'origine avant traitement."
    )
    
    is_suspect: bool = Field(
        default=False, 
        description="Flag d'enquête pour l'analyste SOC."
    )
    
    perimetre_id: Optional[str] = Field(
        default="périmètre-générique", 
        description="Clé étrangère vers le périmètre de sécurité."
    )

    class Config:
        from_attributes = True