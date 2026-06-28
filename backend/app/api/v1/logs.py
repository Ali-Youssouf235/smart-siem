from fastapi import APIRouter, status, HTTPException, Body
from app.schemas.log_schema import LogBaseSchema
from app.core.engine import check_brute_force_ssh, check_lateral_movement
from app.core.database import save_log_to_elasticsearch
# 🟢 NOUVEL IMPORT SEMAINE 3 : Notre parser automatique de logs bruts
from app.services.parser import parse_raw_log 

router = APIRouter(prefix="/api/v1/logs", tags=["Gestion des Logs"])

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_log(log_in: LogBaseSchema):
    try:
        # 1. SAUVEGARDE DIRECTE : Écriture immédiate dans Elasticsearch
        log_dict = log_in.model_dump()
        log_dict["timestamp"] = log_dict["timestamp"].isoformat()
        save_log_to_elasticsearch(log_dict, index_name="smart-siem-logs")

        # 2. Analyse par les filtres du moteur de corrélation
        alerte_bf = check_brute_force_ssh(log_in)
        alerte_ml = check_lateral_movement(log_in)
        
        reponse = {
            "status": "success",
            "message": "Log enregistré dans Elasticsearch et analysé par les règles S3/S6",
            "alerte_declenchee": False,
            "regles_violées": []
        }
        
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


# 🟢 NOUVEAUTÉ SEMAINE 3 : Ingestion de logs textuels bruts (Ex: Sortie syslog en direct)
@router.post("/ingest/raw", status_code=status.HTTP_201_CREATED)
async def ingest_raw_log(raw_log: str = Body(..., media_type="text/plain")):
    """
    Reçoit un log textuel brut, l'analyse via des expressions régulières (Regex),
    le normalise au format standard et l'enregistre DIRECTEMENT dans Elasticsearch.
    """
    try:
        # 1. On passe la ligne brute dans notre usine de parsing
        parsed_data = parse_raw_log(raw_log)
        
        if not parsed_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Le format du log brut n'a pas pu être identifié par le parser regex."
            )
            
        # 2. 🟢 FIX SAUVEGARDE DIRECTE : On prépare le dictionnaire pour Elasticsearch
        # On extrait une copie pour travailler proprement
        log_to_save = dict(parsed_data)
        
        # Formatage de la date en texte ISO pour Elasticsearch
        if hasattr(log_to_save["timestamp"], "isoformat"):
            log_to_save["timestamp"] = log_to_save["timestamp"].isoformat()
        else:
            log_to_save["timestamp"] = str(log_to_save["timestamp"])
            
        # On force l'écriture immédiate dans l'index 'smart-siem-logs'
        save_log_to_elasticsearch(log_to_save, index_name="smart-siem-logs")
        
        # 3. Pour le moteur de corrélation (alertes), on crée le schéma Pydantic de contrôle
        # On passe le timestamp original (qui est un objet datetime grâce à notre modif précédente)
        log_schema = LogBaseSchema(**parsed_data)
        
        # On exécute l'analyse des règles S3/S6 en tâche de fond
        alerte_bf = check_brute_force_ssh(log_schema)
        alerte_ml = check_lateral_movement(log_schema)
        
        # 4. Construction de la réponse Swagger
        reponse = {
            "status": "success",
            "message": f"Log textuel brut normalisé sous l'ID {log_to_save['id']} et enregistré dans Elasticsearch.",
            "format_detecte": log_to_save.get("extra", {}).get("format", "inconnu"),
            "alerte_declenchee": False,
            "regles_violées": []
        }
        
        if alerte_bf:
            reponse["alerte_declenchee"] = True
            reponse["regles_violées"].append("S3_BRUTE_FORCE")
        if alerte_ml:
            reponse["alerte_declenchee"] = True
            reponse["regles_violées"].append("S6_LATERAL_MOVEMENT")
            
        return reponse
        
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Échec de la normalisation et du stockage du log brut : {str(e)}"
        )