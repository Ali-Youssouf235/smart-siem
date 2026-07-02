from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
import time

# Routeur officiel pour FastAPI
router = APIRouter(prefix="/api/v1/agent", tags=["Supervision des Agents SOC"])

# Schéma de réception du Heartbeat
class AgentHeartbeatSchema(BaseModel):
    agent_id: str
    hostname: str
    status: str

# 🟢 Base de données dynamique en mémoire vive (Vide au démarrage)
ACTIVE_AGENTS_CACHE = {}

# --- 1. LISTER LES AGENTS (Pour React) ---
@router.get("", status_code=status.HTTP_200_OK)
async def list_agents():
    """Récupère la liste de tous les agents réels enregistrés."""
    clean_agents_status()
    return {
        "total_agents": len(ACTIVE_AGENTS_CACHE),
        "agents": list(ACTIVE_AGENTS_CACHE.values())
    }

# --- 2. RECEVOIR UN HEARTBEAT (Depuis ton script collecteur.py) ---
@router.post("/heartbeat", status_code=status.HTTP_200_OK)
async def receive_heartbeat(heartbeat: AgentHeartbeatSchema):
    """Réceptionne le signal de vie en direct du script collecteur.py."""
    agent_id = heartbeat.agent_id.upper()
    
    # Enregistrement ou mise à jour en temps réel avec un timestamp
    ACTIVE_AGENTS_CACHE[agent_id] = {
        "id": agent_id,
        "hostname": heartbeat.hostname,
        "os": "Windows Server",
        "status": "online",
        "last_seen_ts": time.time(),  # Sauvegarde du timestamp pour vérification de vie
        "monitored_file": "C:\\ProgramData\\ssh\\logs\\sshd.log"
    }
    return {"status": "acknowledged", "message": f"Heartbeat reçu de {heartbeat.hostname}"}

# --- 🟢 FONCTIONS RECRUTÉES POUR LE DASHBOARD (ALERTS.PY) ---
def clean_agents_status():
    """Supprime du cache les agents qui n'ont pas donné de signal depuis plus de 45 secondes."""
    now = time.time()
    for agent_id, info in list(ACTIVE_AGENTS_CACHE.items()):
        if now - info["last_seen_ts"] > 45:
            del ACTIVE_AGENTS_CACHE[agent_id]

def get_live_agents_count() -> int:
    """Retourne le nombre exact de collecteurs en cours d'exécution."""
    clean_agents_status()
    return len(ACTIVE_AGENTS_CACHE)