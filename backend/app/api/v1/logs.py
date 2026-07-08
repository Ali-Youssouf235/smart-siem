from fastapi import APIRouter, status, HTTPException, Body
from app.schemas.log_schema import LogBaseSchema
from app.core.engine import check_brute_force_ssh, check_lateral_movement
from app.core.database import save_log_to_elasticsearch
from app.services.parser import parse_raw_log 
from app.core.ueba import detect_behavioral_anomalies
from typing import Optional, List
from data.search import search_logs, get_timeline

router = APIRouter(prefix="/api/v1/logs", tags=["Gestion des Logs"])

# --- 1. INGESTION ET ENREGISTREMENT ---
async def ingest_log(log_in: LogBaseSchema):
    """Reçoit un log pré-structuré au format JSON et l'analyse."""
    try:
        # SAUVEGARDE DIRECTE : Écriture immédiate dans Elasticsearch
        log_dict = log_in.model_dump()
        log_dict["timestamp"] = log_dict["timestamp"].isoformat()
        save_log_to_elasticsearch(log_dict, index_name="smart-siem-logs")

        # Analyse par les filtres du moteur de corrélation et UEBA
        alerte_bf = check_brute_force_ssh(log_in)
        alerte_ml = check_lateral_movement(log_in)
        alerte_ueba = detect_behavioral_anomalies(log_dict)
        
        reponse = {
            "status": "success",
            "message": "Log enregistré dans Elasticsearch et analysé par les règles de sécurité",
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

        if alerte_ueba:
            reponse["alerte_declenchee"] = True
            reponse["regles_violées"].append(f"S4_UEBA_{alerte_ueba.regle_id}")
            reponse["details_ueba"] = alerte_ueba
            
        return reponse
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Erreur pendant l'analyse : {str(e)}"
        )


@router.post("/ingest/raw", status_code=status.HTTP_201_CREATED)
async def ingest_raw_log(raw_log: str = Body(..., media_type="text/plain")):
    """Reçoit un log textuel brut, le normalise via Regex et l'analyse."""
    try:
        parsed_data = parse_raw_log(raw_log)
        if not parsed_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Le format du log brut n'a pas pu être identifié par le parser regex."
            )
            
        log_to_save = dict(parsed_data)
        
        if hasattr(log_to_save["timestamp"], "isoformat"):
            log_to_save["timestamp"] = log_to_save["timestamp"].isoformat()
        else:
            log_to_save["timestamp"] = str(log_to_save["timestamp"])
            
        save_log_to_elasticsearch(log_to_save, index_name="smart-siem-logs")
        
        log_schema = LogBaseSchema(**parsed_data)
        alerte_bf = check_brute_force_ssh(log_schema)
        alerte_ml = check_lateral_movement(log_schema)
        alerte_ueba = detect_behavioral_anomalies(parsed_data)
        
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
        if alerte_ueba:
            reponse["alerte_declenchee"] = True
            reponse["regles_violées"].append(f"S4_UEBA_{alerte_ueba.regle_id}")
            reponse["details_ueba"] = alerte_ueba
            
        return reponse
        
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Échec de la normalisation et du stockage du log brut : {str(e)}"
        )


@router.post("/ingest/bulk", status_code=status.HTTP_201_CREATED)
async def ingest_bulk_logs(logs_in: List[LogBaseSchema]):
    """Permet l'ingestion massive de logs (Bulk) optimisée pour les agents de collecte."""
    try:
        for log_in in logs_in:
            log_dict = log_in.model_dump()
            log_dict["timestamp"] = log_dict["timestamp"].isoformat()
            save_log_to_elasticsearch(log_dict, index_name="smart-siem-logs")
        return {"status": "success", "message": f"{len(logs_in)} logs ingérés avec succès en mode bulk."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de l'ingestion par lot (bulk) : {str(e)}"
        )


# --- 2. CONSULTATION ET RECHERCHE ---

@router.get("", status_code=status.HTTP_200_OK)
async def get_all_logs(page: int = 0, size: int = 50):
    """Récupère la liste globale des derniers logs indexés (Page d'accueil)."""
    try:
        return search_logs(page=page, size=size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from typing import Optional

@router.get("/search", status_code=status.HTTP_200_OK)
async def search_multi_criteria(
    source_ip: Optional[str] = None,
    severity: Optional[str] = None, 
    log_type: Optional[str] = None,
    host: Optional[str] = None, 
    date_from: Optional[str] = None, 
    date_to: Optional[str] = None,
    keyword: Optional[str] = None, 
    page: int = 0, 
    size: int = 100
):
    """Moteur de recherche multi-critères Smart SIEM pour le Frontend."""
    try:
        # 🟢 On appelle ta fonction de recherche d'origine sans RIEN modifier à ses paramètres
        result = search_logs(
            source_ip=source_ip, severity=severity, log_type=log_type,
            host=host, date_from=date_from, date_to=date_to,
            keyword=keyword, page=page, size=size
        )
        
        # 🟢 Sécurité pour le Live Feed : Si le résultat est directement une liste, on l'encapsule dans un dictionnaire 
        # pour que Dashboard.jsx s'y retrouve (qu'il reçoive bien un format {"logs": [...]})
        if isinstance(result, list):
            return {"logs": result}
            
        return result

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
@router.get("/timeline", status_code=status.HTTP_200_OK)
async def get_ip_timeline(
    source_ip: Optional[str] = None,
    host: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Génère la Timeline chronologique d'une adresse IP pour l'investigation numérique."""
    try:
        return get_timeline(source_ip=source_ip, host=host, date_from=date_from, date_to=date_to)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_log_by_id(id: str):
    """Récupère le détail complet d'un événement unique via son ID unique log."""
    try:
        res = search_logs(keyword=id, size=1)
        if not res.get("logs"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log introuvable.")
        return res["logs"][0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 3. FILTRAGE RAPIDE ---

@router.get("/severity/critical", status_code=status.HTTP_200_OK)
async def get_critical_logs():
    """Filtre rapide pour charger immédiatement tous les événements à haute criticité."""
    try:
        return search_logs(severity="HIGH", size=50)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/type/auth", status_code=status.HTTP_200_OK)
async def get_auth_logs():
    """Filtre rapide pour charger immédiatement tous les événements d'authentification."""
    try:
        return search_logs(log_type="ssh", size=50)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))