from fastapi import APIRouter, status, HTTPException
from app.schemas.log_schema import LogBaseSchema
from app.core.engine import check_brute_force_ssh

router = APIRouter(prefix="/api/v1/logs", tags=["Gestion des Logs"])

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_log(log_in: LogBaseSchema):
    """
    Endpoint qui reçoit un log, le valide, et l'envoie instantanément au moteur de corrélation.
    """
    try:
        alerte_detectee = check_brute_force_ssh(log_in)
        
        reponse = {
            "status": "success",
            "message": "Log analysé par le moteur de corrélation",
            "alerte_declenchee": False
        }
        
        if alerte_detectee:
            reponse["alerte_declenchee"] = True
            reponse["details_alerte"] = alerte_detectee
            
        return reponse
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Erreur pendant l'analyse : {str(e)}"
        )