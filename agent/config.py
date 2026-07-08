from pathlib import Path

# ==========================
# Répertoire de l'agent
# ==========================

BASE_DIR = Path(__file__).resolve().parent

# ==========================
# API
# ==========================

API_URL = "http://127.0.0.1:8000/api/v1/logs/ingest/raw"
HEARTBEAT_URL = "http://127.0.0.1:8000/api/v1/agent/heartbeat"

# ==========================
# Agent
# ==========================

AGENT_ID = "AGENT-WIN-SSH-01"

HEARTBEAT_INTERVAL = 30
COLLECT_INTERVAL = 2

# ==========================
# Journaux Windows
# ==========================

LOG_CHANNEL = "OpenSSH/Operational"

# ==========================
# Dossiers locaux
# ==========================

LOG_DIR = BASE_DIR / "logs"

LOCAL_LOG_FILE = LOG_DIR / "ssh.log"

STATE_FILE = BASE_DIR / "state.json"