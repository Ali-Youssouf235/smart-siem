# pipeline.py
import uuid, re
from datetime import datetime, timezone
from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"],
                   basic_auth=("elastic", "siem2026"))

# ── Détection automatique des champs ──────────────────────

def detect_log_type(raw: str) -> str:
    raw = raw.lower()
    if any(k in raw for k in ["ssh", "login", "password", "auth", "sudo", "pam"]):
        return "auth"
    if any(k in raw for k in ["iptables", "firewall", "connection", "port", "tcp", "udp"]):
        return "réseau"
    if any(k in raw for k in ["kernel", "systemd", "cron", "disk", "mount"]):
        return "système"
    return "application"

def detect_severity(raw: str) -> str:
    raw = raw.lower()
    if any(k in raw for k in ["failed", "error", "critical", "denied", "attack", "invalid"]):
        return "critical"
    if any(k in raw for k in ["warning", "warn", "refused", "timeout"]):
        return "warning"
    return "info"

def extract_ip(raw: str) -> str | None:
    match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', raw)
    return match.group(0) if match else None

def extract_dest_ip(raw: str) -> str | None:
    # Cherche une 2e IP si elle existe (ex: "from X to Y")
    ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', raw)
    return ips[1] if len(ips) >= 2 else None

# ── Fonction principale d'ingestion ───────────────────────

def ingest_log(
    raw_message: str,
    host: str,
    perimetre_id: str = "perimetre-defaut",
    timestamp: datetime = None
) -> dict:
    """
    Normalise et indexe un log dans Elasticsearch.
    Retourne le document indexé.
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    doc = {
        "id":             str(uuid.uuid4()),
        "timestamp":      timestamp.isoformat(),
        "source_ip":      extract_ip(raw_message),
        "destination_ip": extract_dest_ip(raw_message),
        "host":           host,
        "log_type":       detect_log_type(raw_message),
        "severity":       detect_severity(raw_message),
        "raw_message":    raw_message,
        "is_suspect":     False,          # positionné manuellement par l'analyste
        "perimetre_id":   perimetre_id
    }

    es.index(index="siem-logs", id=doc["id"], document=doc)
    return doc