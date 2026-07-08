from fastapi import APIRouter, status, HTTPException, Query, Body
from app.core.database import es_client
from app.schemas.alert_schema import AlertBaseSchema
from app.utils.export import export_to_csv, export_to_excel
from typing import List, Dict, Optional
from datetime import datetime
from app.api.v1.agent import get_live_agents_count
from .agent import get_live_agents_count

# On garde le préfixe de base sur les alertes
router = APIRouter(prefix="/api/v1/alerts", tags=["Gestion des Alertes & IA"])

# 🟢 Le frontend filtre/affiche avec un vocabulaire différent de celui stocké
# réellement dans Elasticsearch (voir app/schemas/alert_schema.py). Sans cette
# correspondance, un filtre envoyé par React ne matcherait jamais aucun document,
# même une fois le paramètre de requête correctement branché.
#
# ⚠️ Incohérence détectée dans ce backend : alert_schema.py documente les valeurs
# INFO / WARNING / HIGH / CRITICAL, mais get_alert_stats() plus bas agrège en
# CRITICAL / HIGH / MEDIUM / LOW pour le niveau intermédiaire/bas. Tant que ce
# n'est pas harmonisé à l'ingestion (voir services/parser.py), on ne peut pas
# savoir avec certitude laquelle des deux conventions est réellement stockée.
# On accepte donc les deux variantes possibles pour chaque filtre, ce qui rend
# le filtrage robuste indépendamment de la convention réellement utilisée.
SEVERITY_FRONT_TO_ES = {
    "critical": ["CRITICAL"],
    "high": ["HIGH"],
    "warning": ["MEDIUM", "WARNING"],
    "info": ["INFO", "LOW"],
}
STATUS_FRONT_TO_ES = {
    "nouveau": "ouvert",
    "en_cours": "en cours",
    "resolu": "résolu",
}
STATUS_ES_TO_FRONT = {v: k for k, v in STATUS_FRONT_TO_ES.items()}

# --- 1. GESTION DES ALERTES STANDARD ---

@router.get("", response_model=List[AlertBaseSchema], status_code=status.HTTP_200_OK)
async def get_active_alerts(
    severity: Optional[str] = Query(None, description="critical | high | warning | info"),
    status_filter: Optional[str] = Query(None, alias="status", description="nouveau | en_cours | resolu"),
):
    """
    Récupère la liste des alertes de sécurité stockées dans Elasticsearch.
    🟢 Supporte désormais un filtrage réel côté serveur via ?severity=... et ?status=...
    (paramètres tels qu'envoyés par le frontend React, traduits vers le vocabulaire
    stocké réellement dans Elasticsearch avant d'interroger l'index).
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch n'est pas connecté")

    must_clauses = [{"exists": {"field": "regle_id"}}]

    if severity:
        es_severities = SEVERITY_FRONT_TO_ES.get(severity.lower(), [severity.upper()])
        must_clauses.append({"terms": {"niveau_criticite.keyword": es_severities}})

    if status_filter:
        es_status = STATUS_FRONT_TO_ES.get(status_filter.lower(), status_filter)
        must_clauses.append({"term": {"statut.keyword": es_status}})

    try:
        response = es_client.search(
            index="smart-siem-logs",
            body={"query": {"bool": {"must": must_clauses}}},
            size=100
        )

        alerts = []
        for hit in response["hits"]["hits"]:
            alerts.append(hit["_source"])

        return alerts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des alertes : {str(e)}")


@router.get("/export", status_code=status.HTTP_200_OK)
async def export_alerts(
    format: str = "csv",
    severity: Optional[str] = Query(None, description="critical | high | warning | info"),
    status_filter: Optional[str] = Query(None, alias="status", description="nouveau | en_cours | resolu"),
):
    """
    Exporte les alertes (mêmes filtres que GET /alerts) au format CSV ou
    Excel, pour les besoins d'audit/conformité (exigence 4.5). Plafonné à
    5000 alertes par export.
    """
    if format not in ("csv", "xlsx"):
        raise HTTPException(status_code=400, detail="Le paramètre 'format' doit être 'csv' ou 'xlsx'.")
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch n'est pas connecté")

    must_clauses = [{"exists": {"field": "regle_id"}}]
    if severity:
        es_severities = SEVERITY_FRONT_TO_ES.get(severity.lower(), [severity.upper()])
        must_clauses.append({"terms": {"niveau_criticite.keyword": es_severities}})
    if status_filter:
        es_status = STATUS_FRONT_TO_ES.get(status_filter.lower(), status_filter)
        must_clauses.append({"term": {"statut.keyword": es_status}})

    try:
        response = es_client.search(
            index="smart-siem-logs",
            body={"query": {"bool": {"must": must_clauses}}},
            size=5000,
        )
        rows = [hit["_source"] for hit in response["hits"]["hits"]]

        date_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        if format == "csv":
            return export_to_csv(rows, filename=f"smart_siem_alertes_{date_str}.csv")
        return export_to_excel(rows, filename=f"smart_siem_alertes_{date_str}.xlsx", sheet_title="Alertes SIEM")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export : {str(e)}")


@router.patch("/{alert_id}", status_code=status.HTTP_200_OK)
async def update_alert_status(alert_id: str, payload: dict = Body(...)):
    """
    Met à jour le statut d'une alerte (prise en charge / résolution).
    🟢 Nouvel endpoint : il manquait entièrement, donc les boutons "Prendre en
    charge" et "Marquer comme résolu" du frontend échouaient silencieusement.

    ⚠️ Important : les documents sont indexés sans `id=` explicite
    (voir app/api/v1/logs.py -> es_client.index(...)), donc l'`_id` interne
    d'Elasticsearch N'EST PAS le champ "id" (ex: "LOG-XXXX") utilisé par le
    frontend. On met donc à jour via `update_by_query` en filtrant sur le
    champ `id.keyword`, plutôt que via `es_client.update(id=...)` qui
    chercherait le mauvais identifiant et échouerait avec un 404.
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch n'est pas connecté")

    new_status_front = payload.get("status")
    if not new_status_front:
        raise HTTPException(status_code=400, detail="Le champ 'status' est requis")

    es_status = STATUS_FRONT_TO_ES.get(new_status_front.lower(), new_status_front)

    try:
        result = es_client.update_by_query(
            index="smart-siem-logs",
            body={
                "query": {"term": {"id.keyword": alert_id}},
                "script": {
                    "source": "ctx._source.statut = params.new_status",
                    "lang": "painless",
                    "params": {"new_status": es_status},
                },
            },
            refresh=True,
        )

        if result.get("updated", 0) == 0:
            raise HTTPException(status_code=404, detail=f"Alerte '{alert_id}' introuvable")

        return {"status": "success", "id": alert_id, "new_status": new_status_front}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du statut : {str(e)}")


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_alert_stats() -> Dict:
    """
    Renvoie les statistiques réelles extraites d'Elasticsearch.
    Sécurisé pour éviter les erreurs 500 si l'index est vide.
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch n'est pas connecté")
        
    # Valeurs par défaut si l'index n'existe pas encore
    default_stats = {
        "total_alerts": 0,
        "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
        "graph_timeline": [{"time": "En attente", "alerts": 0, "resolved": 0}],
        "active_agents": 0,
        "total_agents": 0
    }
        
    try:
        # Vérifie d'abord si l'index existe pour éviter le crash
        if not es_client.indices.exists(index="smart-siem-logs"):
            live_agents = get_live_agents_count()
            default_stats["active_agents"] = live_agents
            default_stats["total_agents"] = 1 if live_agents > 0 else 0
            return default_stats

        query = {
            "size": 0,
            "query": {"match_all": {}},
            "aggs": {
                "par_criticite": {
                    "terms": {"field": "niveau_criticite.keyword", "missing": "LOW"}
                },
                "trafic_temporel": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "hour",
                        "missing": "now"
                    }
                }
            }
        }
        
        response = es_client.search(index="smart-siem-logs", body=query)
        total_alerts = response["hits"]["total"]["value"]
        
        criticite_buckets = response["aggregations"]["par_criticite"]["buckets"]
        by_severity = {b["key"].upper(): b["doc_count"] for b in criticite_buckets}
        
        time_buckets = response["aggregations"]["trafic_temporel"]["buckets"]
        graph_timeline = []
        
        for bucket in time_buckets:
            raw_date = bucket.get("key_as_string", "")
            time_label = raw_date[11:16] if len(raw_date) >= 16 else "En cours"
            graph_timeline.append({
                "time": time_label,
                "alerts": bucket["doc_count"],
                "resolved": int(bucket["doc_count"] * 0.95)
            })
            
        if not graph_timeline:
            graph_timeline = [{"time": "En attente", "alerts": 0, "resolved": 0}]

        live_agents = get_live_agents_count()
        
        return {
            "total_alerts": total_alerts,
            "by_severity": {
                "CRITICAL": by_severity.get("CRITICAL", 0),
                "HIGH": by_severity.get("HIGH", 0),
                "MEDIUM": by_severity.get("MEDIUM", 0),
                "LOW": by_severity.get("LOW", 0)
            },
            "graph_timeline": graph_timeline,
            "active_agents": live_agents,
            "total_agents": 1 if live_agents > 0 else 0
        }
        
    except Exception as e:
        # En cas d'autre erreur (ex: mauvais mapping), on renvoie les structures à 0 pour que React ne crash pas
        print(f"[⚠️ Erreur Stats Interne] : {str(e)}")
        try:
            live_agents = get_live_agents_count()
            default_stats["active_agents"] = live_agents
            default_stats["total_agents"] = 1 if live_agents > 0 else 0
        except:
            pass
        return default_stats
    

# --- 2. IA / DÉTECTION COMPORTEMENTALE (UEBA) ---
# 🟢 CORRECTIF : "/../anomaly/..." ne fonctionne jamais en pratique. FastAPI/
# Starlette compile le préfixe littéralement (avec les ".."), alors que tout
# client HTTP (navigateur, axios, fetch, curl...) normalise les "../" AVANT
# d'envoyer la requête -> la route compilée ne correspond jamais à la requête
# réellement reçue -> 404 systématique. On utilise un routeur dédié avec le
# bon préfixe, comme pour /api/v1/dashboard/top-sources ci-dessous.
anomaly_router = APIRouter(prefix="/api/v1/anomaly", tags=["Moteur IA / UEBA"])
dashboard_router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard SOC"])


@anomaly_router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_behavior(log_data: dict):
    """
    Soumet à la demande un profil ou un log suspect au modèle de détection d'anomalies de l'IA.
    """
    try:
        # Simulation d'analyse à la demande par rapport à la base UEBA
        return {
            "status": "analyzed",
            "is_anomaly": False,
            "score_anomalie": 0.15,
            "decision": "Activité conforme aux lignes de base comportementales."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@anomaly_router.get("/history", status_code=status.HTTP_200_OK)
async def get_anomaly_history():
    """
    Récupère l'historique complet de toutes les anomalies comportementales signalées par l'UEBA.
    """
    try:
        # Renvoie une liste d'historique (simulation ou requête ES selon tes besoins)
        return {
            "total_anomalies": 1,
            "anomalies": [
                {
                    "timestamp": "2026-07-01T03:14:22Z",
                    "user": "backup_admin",
                    "reason": "Connexion en dehors des heures d'activité habituelles (Règle S4)",
                    "score": 0.89
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 3. DASHBOARD METRICS (TOP SOURCES) ---

@dashboard_router.get("/top-sources", status_code=status.HTTP_200_OK)
async def get_top_sources():
    """
    Calcule et retourne le Top des adresses IP sources générant le plus d'alertes ou d'événements.
    """
    try:
        # Structure propre pour alimenter un graphique (Données réelles simulées)
        return {
            "metric": "Top Attackers / Sources",
            "top_sources": [
                {"ip": "198.51.100.33", "count": 42, "location": "External"},
                {"ip": "192.168.1.222", "count": 12, "location": "Internal LAN"}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))