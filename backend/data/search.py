from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"],
                   basic_auth=("elastic", "siem2026"))

def search_logs(
        source_ip: str = None,
        severity: str = None,
        log_type: str = None,
        host: str = None,
        username: str = None,
        date_from: str = None,
        date_to: str = None,
        is_suspect: bool = None,
        keyword: str = None,
        perimetre_id: str = None,
        size: int = 100,
        page: int = 0
) -> dict:
    """
    Moteur de recherche universel Smart SIEM.
    Optimisé pour tolérer les formats de recherche flous du frontend.

    🟢 `perimetre_id` : filtre EXACT (contrairement au `keyword` flou plus bas)
    utilisé pour le cloisonnement des accès (RBAC 4.7) — un rôle "lecteur"
    lié à un périmètre donné ne doit voir QUE les logs de ce périmètre.
    """
    filters = []

    # --- FILTRES EXACTS ---
    if source_ip:
        filters.append({"match": {"source_ip": source_ip}})
    if severity:
        filters.append({"match": {"severity": severity}})
    if log_type:
        filters.append({"match": {"log_type": log_type}})
    if host:
        filters.append({"match": {"host": host}})
    if is_suspect is not None:
        filters.append({"term": {"is_suspect": is_suspect}})
    if username:
        filters.append({"match": {"username": username}})
    if perimetre_id:
        filters.append({"term": {"perimetre_id.keyword": perimetre_id}})

    # --- RECHERCHE GLOBALE DYNAMIQUE (Le correctif principal) ---
    if keyword:
        keyword_str = str(keyword).strip()
        
        # CAS A : L'analyste cherche un timestamp complet ou partiel
        if "-" in keyword_str and ("T" in keyword_str or ":" in keyword_str):
            filters.append({"match": {"timestamp": keyword_str}})
            
        # CAS B : L'analyste cherche un ID de log
        elif keyword_str.startswith("LOG-"):
            filters.append({"match": {"id": keyword_str}})
            
        # CAS C : Recherche sur n'importe quel attribut (Souple et permissif)
        else:
            filters.append({
                "multi_match": {
                    "query": keyword_str,
                    "fields": [
                        "id^3", 
                        "raw_message", 
                        "host", 
                        "severity", 
                        "log_type", 
                        "perimetre_id"
                    ],
                    "operator": "or",  # <-- "or" permet de trouver le log dès qu'un des mots correspond !
                    "fuzziness": "AUTO"
                }
            })

    # --- FILTRE TEMPOREL ---
    if date_from or date_to:
        date_range = {"range": {"timestamp": {}}}
        if date_from: date_range["range"]["timestamp"]["gte"] = date_from
        if date_to: date_range["range"]["timestamp"]["lte"] = date_to
        filters.append(date_range)

    # Construction de la requête Booléenne
    query = {"bool": {"must": filters}} if filters else {"match_all": {}}

    result = es.search(
        index="smart-siem-logs",
        body={
            "query": query,
            "sort": [{"timestamp": {"order": "desc"}}],
            "size": size,
            "from": page * size
        }
    )

    return {
        "total": result["hits"]["total"]["value"],
        "logs": [hit["_source"] for hit in result["hits"]["hits"]]
    }

def get_timeline(
    source_ip: str = None,
    host:      str = None,
    date_from: str = None,
    date_to:   str = None
) -> dict:
    filters = []
    if source_ip: filters.append({"term": {"source_ip": source_ip}})
    if host:      filters.append({"term": {"host":      host}})
    if date_from or date_to:
        range_filter = {"range": {"timestamp": {}}}
        if date_from: range_filter["range"]["timestamp"]["gte"] = date_from
        if date_to:   range_filter["range"]["timestamp"]["lte"] = date_to
        filters.append(range_filter)

    result = es.search(
        index="smart-siem-logs",
        body={
            "query": {"bool": {"must": filters}},
            "sort":  [{"timestamp": "asc"}],
            "size":  500
        }
    )

    hits = [hit["_source"] for hit in result["hits"]["hits"]]

    for i in range(1, len(hits)):
        from datetime import datetime
        t1 = datetime.fromisoformat(hits[i-1]["timestamp"].replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(hits[i]["timestamp"].replace("Z", "+00:00"))
        hits[i]["delta_seconds"] = int((t2 - t1).total_seconds())

    return {"total": len(hits), "timeline": hits}

def mark_suspect(log_id: str, is_suspect: bool = True) -> dict:
    result = es.update(
        index="smart-siem-logs",
        id=log_id,
        body={"doc": {"is_suspect": is_suspect}}
    )
    return {"id": log_id, "is_suspect": is_suspect, "result": result["result"]}

def get_suspects(size: int = 100) -> dict:
    return search_logs(is_suspect=True, size=size)

import time
import requests
import os
from datetime import datetime

# Configuration locale (Synchronisée au singulier)
LOG_FILE_PATH = r"C:\ProgramData\ssh\logs\sshd.log"
API_URL = "http://127.0.0.1:8000/api/v1/logs/ingest/raw"
HEARTBEAT_URL = "http://127.0.0.1:8000/api/v1/agent/heartbeat"

# Couleurs ANSI
C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_CYAN = "\033[96m"
C_END = "\033[0m"
C_BOLD = "\033[1m"

def get_time():
    return f"{C_BLUE}[{datetime.now().strftime('%H:%M:%S')}]{C_END}"

def send_heartbeat():
    try:
        payload = {"agent_id": "AGENT-WIN-SSHD-01", "hostname": "Windows-Server-Target", "status": "online"}
        requests.post(HEARTBEAT_URL, json=payload, timeout=2)
        print(f"{get_time()} {C_GREEN}{C_BOLD}[HEARTBEAT]{C_END} Signal de vie與Manager synchronisé.")
    except Exception:
        print(f"{get_time()} {C_YELLOW}{C_BOLD}[HEARTBEAT]{C_END} Serveur SIEM injoignable.")

# ─────────────────────────────────────────────────────────────────────────────
# BANNIÈRE D'ACCUEIL
# ─────────────────────────────────────────────────────────────────────────────
print(f"{C_CYAN}{C_BOLD}" + "=" * 65 + f"{C_END}")
print(f"{C_CYAN}{C_BOLD} 🛡️   SMART SIEM — AGENT DE COLLECTE WINDOWS (CIBLE){C_END}")
print(f"{C_CYAN}{C_BOLD}" + "=" * 65 + f"{C_END}")
print(f" {C_BOLD}[*]{C_END} Target Logfile : {C_YELLOW}{LOG_FILE_PATH}{C_END}")
print(f" {C_BOLD}[*]{C_END} SIEM Endpoint  : {C_YELLOW}{API_URL}{C_END}")
print(f"{C_CYAN}" + "─" * 65 + f"{C_END}")

# Création du fichier de simulation s'il manque
#if not os.path.exists(LOG_FILE_PATH):
#    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
#   with open(LOG_FILE_PATH, "w") as tmp: pass
#   print(f"{get_time()} {C_GREEN}{C_BOLD}[CREATION]{C_END} Fichier de simulation généré.")

print(f"{get_time()} {C_GREEN}{C_BOLD}[READY]{C_END} Écoute active lancée...\n")

# Premier signal au démarrage
send_heartbeat()

def tail_and_send():
    with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        last_heartbeat = time.time()
        
        while True:
            # Heartbeat toutes les 30 secondes
            if time.time() - last_heartbeat > 30:
                send_heartbeat()
                last_heartbeat = time.time()

            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            
            clean_line = line.strip()
            if clean_line:
                print(f"{get_time()} {C_BOLD}[DETECTED]{C_END} {clean_line[:65]}...")
                try:
                    headers = {"Content-Type": "text/plain"}
                    response = requests.post(API_URL, data=clean_line.encode('utf-8'), headers=headers)
                    if response.status_code in [200, 201]:
                        print(f"        └──> {C_GREEN}{C_BOLD}[SUCCESS]{C_END} Transmis à l'index SIEM (HTTP {response.status_code})")
                    else:
                        print(f"        └──> {C_RED}{C_BOLD}[REFUSED]{C_END} Code d'erreur (HTTP {response.status_code})")
                except Exception as e:
                    print(f"        └──> {C_RED}{C_BOLD}[FAILURE]{C_END} Connexion impossible : {str(e)}")

if __name__ == "__main__":
    try:
        tail_and_send()
    except KeyboardInterrupt:
        print(f"\n{get_time()} {C_YELLOW}{C_BOLD}[SHUTDOWN]{C_END} Arrêt propre de l'agent.")

def count_events_for_correlation(
    source_ip:  str,
    keyword:    str,
    timeframe:  int 
) -> int:
    result = es.count(
        index="smart-siem-logs",
        body={
            "query": {
                "bool": {
                    "must": [
                        {"match": {"raw_message": keyword}},
                        {"term":  {"source_ip":   source_ip}},
                        {"range": {"timestamp":   {"gte": f"now-{timeframe}s"}}}
                    ]
                }
            }
        }
    )
    return result["count"]