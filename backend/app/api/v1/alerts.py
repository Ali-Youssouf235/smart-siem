from fastapi import APIRouter, status
from app.schemas.alert_schema import AlertBaseSchema
from app.core.engine import ALERTE_STORAGE_GLOBAL # On l'importe depuis l'engine
from typing import List

router = APIRouter(prefix="/api/v1/alerts", tags=["Gestion des Alertes"])

@router.get("", response_model=List[AlertBaseSchema], status_code=status.HTTP_200_OK)
async def get_active_alerts():
    """
    Renvoie la liste de toutes les alertes de sécurité détectées par le moteur.
    """
    return ALERTE_STORAGE_GLOBAL