from fastapi import APIRouter, status
from app.schemas.alert_schema import AlertBaseSchema
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/v1/alerts", tags=["Gestion des Alertes"])

@router.get("", response_model=List[AlertBaseSchema], status_code=status.HTTP_200_OK)
async def get_active_alerts():
    """
    Endpoint appelé par le Frontend Vue.js pour récupérer les alertes de sécurité de la Crisis Room.
    """
    # Pour la Semaine 1, comme la BDD n'est pas branchée, on renvoie une fausse alerte de test
    # pour que ton pote du Frontend puisse tester ses composants Vue.js !
    fake_alert = {
        "id": "ALT-SIMULATED-2026",
        "timestamp": datetime.utcnow(),
        "niveau_criticite": "CRITICAL",
        "statut": "ouvert",
        "regle_id": "MITRE-T1110-BRUTEFORCE",
        "utilisateur_id": None
    }
    
    return [fake_alert]