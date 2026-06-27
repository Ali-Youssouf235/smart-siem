from fastapi import APIRouter, status
from app.schemas.alert_schema import AlertBaseSchema
from app.core.engine import ALERTE_STORAGE_GLOBAL
from typing import List, Dict

router = APIRouter(prefix="/api/v1/alerts", tags=["Gestion des Alertes"])

@router.get("", response_model=List[AlertBaseSchema], status_code=status.HTTP_200_OK)
async def get_active_alerts():
    """Renvoie la liste de toutes les alertes de sécurité détectées."""
    return ALERTE_STORAGE_GLOBAL

# NOUVEAU LIVRABLE : Route pour le tableau de bord du Front-end
@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_alert_stats() -> Dict:
    """
    Renvoie les statistiques agrégées des alertes pour les graphiques du dashboard.
    """
    total_alerts = len(ALERTE_STORAGE_GLOBAL)
    
    # Comptage par niveau de criticité
    critical_count = sum(1 for a in ALERTE_STORAGE_GLOBAL if a.niveau_criticite == "CRITICAL")
    high_count = sum(1 for a in ALERTE_STORAGE_GLOBAL if a.niveau_criticite == "HIGH")
    medium_count = sum(1 for a in ALERTE_STORAGE_GLOBAL if a.niveau_criticite == "MEDIUM")
    
    return {
        "total_alerts": total_alerts,
        "by_severity": {
            "CRITICAL": critical_count,
            "HIGH": high_count,
            "MEDIUM": medium_count
        },
        "status_summary": {
            "ouvert": sum(1 for a in ALERTE_STORAGE_GLOBAL if a.statut == "ouvert"),
            "en_cours": sum(1 for a in ALERTE_STORAGE_GLOBAL if a.statut == "en_cours"),
            "resolu": sum(1 for a in ALERTE_STORAGE_GLOBAL if a.statut == "resolu")
        }
    }