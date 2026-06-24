from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import logs, alerts # On importe tes deux fichiers de routes

app = FastAPI(
    title="Smart SIEM - CTU API Backend",
    description="Moteur d'ingestion et de corrélation des événements de sécurité de la CTU",
    version="1.0.0"
)

# Config CORS : indispensable pour que l'application Vue.js du Front ait le droit de te parler
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En développement, on accepte tout le monde
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# On enregistre les routes dans l'application principale
app.include_router(logs.router)
app.include_router(alerts.router)

@app.get("/health", tags=["Infrastructure"])
async def health_check():
    """Vérifie que l'API fonctionne bien."""
    return {"status": "healthy", "environment": "Cellule CTU Active"}