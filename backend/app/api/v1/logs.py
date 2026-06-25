from fastapi import APIRouter, status, HTTPException
from app.schemas.log_schema import LogBaseSchema
from app.core.engine import check_brute_force_ssh, check_lateral_movement

router = APIRouter(prefix="/api/v1/logs", tags=["Gestion des Logs"])

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_log(log_in: LogBaseSchema):
    try:
        # On passe le log dans les deux filtres du moteur de corrélation
        alerte_bf = check_brute_force_ssh(log_in)
        alerte_ml = check_lateral_movement(log_in)
        
        reponse = {
            "status": "success",
            "message": "Log analysé par les règles de corrélation S3 et S6",
            "alerte_declenchee": False,
            "regles_violées": []
        }
        
        # Si l'une des deux règles a mordu, on lève l'alerte
        if alerte_bf:
            reponse["alerte_declenchee"] = True
            reponse["regles_violées"].append("S3_BRUTE_FORCE")
            reponse["details_brute_force"] = alerte_bf
            
        if alerte_ml:
            reponse["alerte_declenchee"] = True
            reponse["regles_violées"].append("S6_LATERAL_MOVEMENT")
            reponse["details_mouvement_lateral"] = alerte_ml
            
        return reponse
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Erreur pendant l'analyse : {str(e)}"
        )