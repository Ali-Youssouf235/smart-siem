from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1 import logs, alerts 
from app.core.database import es_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Logique exécutée au démarrage du Backend
    if es_client:
        print("🔌 Connexion validée vers le cluster Elasticsearch au démarrage.")
    yield
    # Logique exécutée à la fermeture du Backend (si nécessaire)

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

@app.get("/health", tags=["Infrastructure"])
async def health_check():
    """Vérifie que l'API fonctionne bien."""
    db_status = "connected" if es_client else "disconnected"
    return {
        "status": "healthy", 
        "environment": "Cellule CTU Active",
        "database": db_status
    }