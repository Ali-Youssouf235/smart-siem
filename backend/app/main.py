import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1 import logs, alerts, rules, agent, auth, retention  # 🟢 AJOUT DES MODULES
from app.core.database import es_client
from app.api.v1.reports import router as reports_router
from app.api.v1.alerts import anomaly_router, dashboard_router  # 🟢 CORRECTIF routes /../

# 🟢 Intervalle de la purge automatique de fond (en secondes). Une valeur basse
# (60s) permet de démontrer en direct qu'une politique de rétention courte
# (ex: 1h) est bien appliquée en continu, et pas seulement au moment du
# changement de configuration.
RETENTION_CHECK_INTERVAL_SECONDS = 60
REPORT_SCHEDULE_CHECK_INTERVAL_SECONDS = 300  # 5 minutes suffisent pour une granularité à l'heure


async def retention_background_loop():
    """Purge périodiquement les logs expirés selon la politique de rétention active."""
    while True:
        try:
            deleted = retention.purge_expired_logs()
            if deleted:
                print(f"🗑️ [Rétention] {deleted} log(s) expiré(s) purgé(s) automatiquement.")
        except Exception as e:
            print(f"⚠️ [Rétention] Erreur dans la boucle de purge automatique : {e}")
        await asyncio.sleep(RETENTION_CHECK_INTERVAL_SECONDS)


async def report_schedule_background_loop():
    """
    Vérifie périodiquement si un rapport PDF automatique (quotidien/hebdo)
    doit être généré maintenant, selon la planification configurée via
    PUT /api/v1/reports/schedule, et l'archive le cas échéant.
    """
    from app.api.v1 import reports as reports_module
    from app.services.report_service import generate_and_archive_report
    from datetime import datetime, timedelta

    while True:
        try:
            schedule = reports_module._get_schedule()
            frequency = schedule.get("frequency", "disabled")

            if frequency != "disabled" and es_client:
                now = datetime.utcnow()
                last_run_str = schedule.get("last_run")
                last_run = datetime.fromisoformat(last_run_str) if last_run_str else None

                due = False
                if now.hour == schedule.get("hour", 7):
                    if frequency == "daily":
                        due = last_run is None or (now - last_run) >= timedelta(hours=20)
                    elif frequency == "weekly":
                        due = last_run is None or (now - last_run) >= timedelta(days=6, hours=20)

                if due:
                    report_type = "auto_quotidien" if frequency == "daily" else "auto_hebdomadaire"
                    generate_and_archive_report(report_type=report_type)
                    schedule["last_run"] = now.isoformat()
                    es_client.index(
                        index=reports_module.INDEX_CONFIG,
                        id=reports_module.SCHEDULE_DOC_ID,
                        document=schedule,
                        refresh="wait_for",
                    )
                    print(f"📄 [Rapports] Rapport {report_type} généré et archivé automatiquement.")
        except Exception as e:
            print(f"⚠️ [Rapports] Erreur dans la boucle de planification : {e}")
        await asyncio.sleep(REPORT_SCHEDULE_CHECK_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Logique exécutée au démarrage du Backend
    if es_client:
        print("🔌 Connexion validée vers le cluster Elasticsearch au démarrage.")
    retention_task = asyncio.create_task(retention_background_loop())
    report_task = asyncio.create_task(report_schedule_background_loop())
    yield
    retention_task.cancel()
    report_task.cancel()

app = FastAPI(
    title="Smart SIEM - CTU API Backend",
    description="Moteur d'ingestion et de corrélation des événements de sécurité de la CTU",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS pour la future connexion avec le Frontend Vue.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement officiel des routeurs
app.include_router(logs.router)
app.include_router(alerts.router)
app.include_router(rules.router)   # 🟢 INCLUSION DES RÈGLES
app.include_router(agent.router)  # 🟢 INCLUSION DES AGENTS
app.include_router(auth.router)    # 🟢 INCLUSION AUTH & USERS
app.include_router(reports_router)
app.include_router(anomaly_router)     # 🟢 CORRECTIF : anciennement /api/v1/alerts/../anomaly/*
app.include_router(dashboard_router)   # 🟢 CORRECTIF : anciennement /api/v1/alerts/../dashboard/*
app.include_router(retention.router)   # 🟢 POLITIQUE DE RÉTENTION DES LOGS

@app.get("/health", tags=["Infrastructure"])
async def health_check():
    """Vérifie que l'API fonctionne bien."""
    db_status = "connected" if es_client else "disconnected"
    return {
        "status": "healthy", 
        "environment": "Cellule CTU Active",
        "database": db_status
    }