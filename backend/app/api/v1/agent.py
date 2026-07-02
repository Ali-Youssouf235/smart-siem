from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from datetime import datetime

# Routeur officiel pour FastAPI
router = APIRouter(prefix="/api/v1/agent", tags=["Supervision des Agents SOC"])

# Schéma de réception du Heartbeat
class AgentHeartbeatSchema(BaseModel):
    agent_id: str
    hostname: str
    status: str

# Base de données temporaire en mémoire
SIMULATED_AGENTS = {
    "AGENT-WIN-SSHD-01": {
        "id": "AGENT-WIN-SSHD-01",
        "hostname": "Windows-Server-Target",
        "os": "Windows",
        "status": "online",
        "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "monitored_file": "C:\\Users\\CHECK SERVICE\\Desktop\\PROGET INTERGRATEUR\\sshd_fake.log"
    }
}

# --- 1. LISTER LES AGENTS (Pour React) ---
@router.get("", status_code=status.HTTP_200_OK)
async def list_agents():
    """Récupère la liste de tous les agents de collecte enregistrés."""
    return {
        "total_agents": len(SIMULATED_AGENTS),
        "agents": list(SIMULATED_AGENTS.values())
    }

# --- 2. RECOIVRE UN HEARTBEAT (Depuis le script de collecte) ---
@router.post("/heartbeat", status_code=status.HTTP_200_OK)
async def receive_heartbeat(heartbeat: AgentHeartbeatSchema):
    """Réceptionne le signal de vie de la machine cible."""
    agent_id = heartbeat.agent_id.upper()
    
    if agent_id in SIMULATED_AGENTS:
        SIMULATED_AGENTS[agent_id]["status"] = "online"
        SIMULATED_AGENTS[agent_id]["last_seen"] = datetime.now().strftime("%H:%M:%S")
        return {"status": "acknowledged", "message": f"Heartbeat reçu de {heartbeat.hostname}"}
    
    # Auto-enregistrement si inconnu
    SIMULATED_AGENTS[agent_id] = {
        "id": agent_id,
        "hostname": heartbeat.hostname,
        "os": "Windows (Auto-Detected)",
        "status": "online",
        "last_seen": datetime.now().strftime("%H:%M:%S"),
        "monitored_file": "Simulated Path"
    }
    return {"status": "registered", "message": "Nouvel agent enregistré."}