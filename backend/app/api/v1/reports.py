from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, Response
from app.services.report_service import generate_security_pdf, archive_generated_report, INDEX_REPORTS_ARCHIVE
from app.core.database import es_client
from datetime import datetime
import os
import base64

router = APIRouter(prefix="/api/v1/reports", tags=["Rapports de Sécurité"])

INDEX_CONFIG = "smart-siem-config"
SCHEDULE_DOC_ID = "report_schedule"
DEFAULT_SCHEDULE = {"frequency": "disabled", "hour": 7, "last_run": None}


@router.get("/generate", response_class=FileResponse)
async def download_security_report():
    """
    Génère de manière dynamique un rapport d'activité PDF consolidé basé
    sur les logs et alertes Elasticsearch, le renvoie en téléchargement,
    ET l'archive automatiquement (visible ensuite dans /reports/archive).
    """
    try:
        pdf_path = generate_security_pdf()

        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Le fichier PDF n'a pas pu être généré sur le serveur.",
            )

        archive_generated_report(pdf_path, report_type="manuel")

        return FileResponse(
            path=pdf_path,
            filename=f"smart_siem_report_{datetime.utcnow().strftime('%Y%m%d')}.pdf",
            media_type="application/pdf",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la création du rapport PDF : {str(e)}",
        )


# ─────────────────────────────────────────────────────────────────────────
# HISTORIQUE DES LIVRABLES (remplace la liste factice codée en dur au Frontend)
# ─────────────────────────────────────────────────────────────────────────

@router.get("/archive", status_code=status.HTTP_200_OK)
async def list_archived_reports(limit: int = 20):
    """Liste les rapports déjà générés (manuels ou automatiques), les plus récents d'abord."""
    if not es_client:
        return {"total": 0, "reports": []}
    try:
        if not es_client.indices.exists(index=INDEX_REPORTS_ARCHIVE):
            return {"total": 0, "reports": []}

        result = es_client.search(
            index=INDEX_REPORTS_ARCHIVE,
            body={
                "query": {"match_all": {}},
                "sort": [{"generated_at": {"order": "desc"}}],
                "size": limit,
                "_source": {"excludes": ["pdf_base64"]},  # métadonnées seulement, pas le binaire
            },
        )
        reports = []
        for hit in result["hits"]["hits"]:
            src = hit["_source"]
            src["id"] = hit["_id"]
            reports.append(src)
        return {"total": len(reports), "reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lecture de l'historique : {str(e)}")


@router.get("/archive/{doc_id}/download")
async def download_archived_report(doc_id: str):
    """Télécharge un rapport PDF précédemment archivé."""
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")
    try:
        result = es_client.get(index=INDEX_REPORTS_ARCHIVE, id=doc_id, ignore=[404])
        if not result or not result.get("found"):
            raise HTTPException(status_code=404, detail="Rapport introuvable dans l'archive.")

        src = result["_source"]
        pdf_bytes = base64.b64decode(src["pdf_base64"])
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{src.get("filename", "rapport.pdf")}"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur téléchargement : {str(e)}")


# ─────────────────────────────────────────────────────────────────────────
# PLANIFICATION AUTOMATIQUE (quotidien / hebdomadaire / désactivé)
# ─────────────────────────────────────────────────────────────────────────

@router.get("/schedule", status_code=status.HTTP_200_OK)
async def get_report_schedule():
    """Renvoie la planification actuelle de génération automatique des rapports."""
    return _get_schedule()


@router.put("/schedule", status_code=status.HTTP_200_OK)
async def set_report_schedule(payload: dict):
    """
    Configure la génération automatique :
    {"frequency": "daily" | "weekly" | "disabled", "hour": 0-23}
    Le rapport sera ensuite généré et archivé tout seul par la tâche de
    fond (voir main.py), sans action manuelle, à l'heure choisie.
    """
    frequency = payload.get("frequency")
    hour = payload.get("hour", 7)

    if frequency not in ("daily", "weekly", "disabled"):
        raise HTTPException(status_code=400, detail="'frequency' doit être 'daily', 'weekly' ou 'disabled'.")
    if not isinstance(hour, int) or not (0 <= hour <= 23):
        raise HTTPException(status_code=400, detail="'hour' doit être un entier entre 0 et 23.")
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")

    current = _get_schedule()
    new_schedule = {"frequency": frequency, "hour": hour, "last_run": current.get("last_run")}
    es_client.index(index=INDEX_CONFIG, id=SCHEDULE_DOC_ID, document=new_schedule, refresh="wait_for")

    return {"status": "success", "message": "Planification mise à jour.", "schedule": new_schedule}


def _get_schedule() -> dict:
    if not es_client:
        return DEFAULT_SCHEDULE
    try:
        result = es_client.get(index=INDEX_CONFIG, id=SCHEDULE_DOC_ID, ignore=[404])
        if result and result.get("found"):
            return result["_source"]
    except Exception:
        pass
    return DEFAULT_SCHEDULE
