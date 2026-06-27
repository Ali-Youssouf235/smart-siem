from fastapi import APIRouter, status, HTTPException
from app.core.database import es_client
from app.schemas.alert_schema import AlertBaseSchema
from typing import List, Dict

router = APIRouter(prefix="/api/v1/alerts", tags=["Gestion des Alertes"])

@router.get("", response_model=List[AlertBaseSchema], status_code=status.HTTP_200_OK)
async def get_active_alerts():
    """
    Récupère la liste de toutes les alertes de sécurité stockées dans Elasticsearch.
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch n'est pas connecté")
        
    try:
        # On fait une recherche globale pour ramener les 100 dernières alertes
        # Note : On cherche dans 'smart-siem-logs' car les alertes y sont indexées,
        # ou remplace par "smart-siem-alerts" si tu as créé un index dédié.
        response = es_client.search(
            index="smart-siem-logs", 
            body={"query": {"exists": {"field": "regle_id"}}}, # On filtre pour n'avoir que des alertes
            size=100
        )
        
        alerts = []
        for hit in response["hits"]["hits"]:
            alerts.append(hit["_source"])
            
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des alertes : {str(e)}")


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_alert_stats() -> Dict:
    """
    Renvoie les statistiques agrégées et dynamiques calculées par Elasticsearch
    pour alimenter les graphiques en temps réel du dashboard Vue.js.
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch n'est pas connecté")
        
    try:
        # Requête d'agrégation Elasticsearch (demande des compteurs sans les documents bruts)
        query = {
            "size": 0,
            "query": {"exists": {"field": "regle_id"}}, # Uniquement les documents de type alerte
            "aggs": {
                "par_criticite": {
                    "terms": {"field": "niveau_criticite.keyword"}
                },
                "par_statut": {
                    "terms": {"field": "statut.keyword"}
                }
            }
        }
        
        response = es_client.search(index="smart-siem-logs", body=query)
        
        # Extraction du total global
        total_alerts = response["hits"]["total"]["value"]
        
        # Extraction des groupes (buckets) calculés par Elasticsearch
        criticite_buckets = response["aggregations"]["par_criticite"]["buckets"]
        by_severity = {b["key"]: b["doc_count"] for b in criticite_buckets}
        
        statut_buckets = response["aggregations"]["par_statut"]["buckets"]
        status_summary = {b["key"]: b["doc_count"] for b in statut_buckets}
        
        # Structuration de la réponse finale pour le Frontend
        return {
            "total_alerts": total_alerts,
            "by_severity": {
                "CRITICAL": by_severity.get("CRITICAL", 0),
                "HIGH": by_severity.get("HIGH", 0),
                "MEDIUM": by_severity.get("MEDIUM", 0)
            },
            "status_summary": {
                "ouvert": status_summary.get("ouvert", 0),
                "en_cours": status_summary.get("en_cours", 0),
                "resolu": status_summary.get("resolu", 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des statistiques : {str(e)}")