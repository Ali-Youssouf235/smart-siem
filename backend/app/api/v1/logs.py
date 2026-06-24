from fastapi import APIRouter, status, HTTPException
from app.schemas.log_schema import LogBaseSchema
from app.core.engine import check_brute_force_ssh  # On importe notre moteur
from typing import List

router = APIRouter(prefix="/api/v1/logs", tags=["Gestion des Logs"])

# On va stocker les alertes générées dans une liste pour que la route des alertes puisse les lire
ALERTE_STORAGE: List[dict] = []

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_log(log_in: LogBaseSchema):
    """
    Endpoint qui reçoit un log, le valide, et l'envoie instantanément au moteur de corrélation.
    """
    try:
        # On envoie le log dans le cerveau du SIEM (le moteur de corrélation)
        alerte_detectee = check_brute_force_ssh(log_in)
        
        reponse = {
            "status": "success",
            "message": "Log analysé par le moteur de corrélation",
            "alerte_declenchee": False
        }
        
        # Si le moteur a détecté une attaque, on enregistre l'alerte
        if alerte_detectee:
            from app.api.v1.alerts import ALERTE_STORAGE_GLOBAL
            ALERTE_STORAGE_GLOBAL.append(alerte_detectee.dict())
            reponse["alerte_declenchee"] = True
            reponse["details_alerte"] = alerte_detectee
            
        return reponse
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Erreur pendant l'analyse : {str(e)}"
        )