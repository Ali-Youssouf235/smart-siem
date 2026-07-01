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
        size: int = 100,
        page: int = 0
) -> dict:

    """
    Moteur de recherche univesel.
    Chaque paramètre est optionnel - on combine uniquement ceux fournis
    :param source_ip:
    :param severity:
    :param log_type:
    :param host:
    :param usernamen:
    :param date_from:
    :param date_to:
    :param is_suspect:
    :param keyword:
    :param size:
    :param page:
    :return:
    """
    filters = []

    if source_ip:
        filters.append({"term": {"source_ip": source_ip}})
    if severity:
        filters.append({"term": {"severity": severity}})
    if log_type:
        filters.append({"term": {"log_type": log_type}})
    if host:
        filters.append({"term": {"host": host}})
    if is_suspect is not None:
        filters.append({"term": {"is_suspect": is_suspect}})

    if username:
        filters.append({"term": {"username": username}})
    if keyword: filters.append({"match": {"raw_message": keyword}})

    if date_from or date_to:
        date_range = {"range": {}}
        if date_from: date_range["range"]["timestamp"] = {"gte": date_from}
        if date_to: date_range["range"]["timestamp"] = {"lte": date_to}
        filters.append(date_range)

    query = {"bool": {"must": filters}} if filters else {"match_all": {}}

    result = es.search(index="smart-siem-logs",
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
    """
    Reconstitue la séquence chronologique des événements
    pour une IP ou une machine donnée.
    """
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
            "sort":  [{"timestamp": "asc"}],    # ordre chronologique ascendant
            "size":  500
        }
    )

    hits = [hit["_source"] for hit in result["hits"]["hits"]]

    # Calcule le delta entre chaque événement pour visualiser les gaps
    for i in range(1, len(hits)):
        from datetime import datetime
        t1 = datetime.fromisoformat(hits[i-1]["timestamp"].replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(hits[i]["timestamp"].replace("Z", "+00:00"))
        hits[i]["delta_seconds"] = int((t2 - t1).total_seconds())

    return {"total": len(hits), "timeline": hits}

def mark_suspect(log_id: str, is_suspect: bool = True) -> dict:
    """
    Marque ou démarque un log comme suspect.
    Appelée par le backend quand un analyste clique sur le bouton dans l'UI.
    """
    result = es.update(
        index="smart-siem-logs",
        id=log_id,
        body={"doc": {"is_suspect": is_suspect}}
    )
    return {"id": log_id, "is_suspect": is_suspect, "result": result["result"]}


def get_suspects(size: int = 100) -> dict:
    """Retourne tous les logs marqués comme suspects, du plus récent au plus ancien."""
    return search_logs(is_suspect=True, size=size)

def count_events_for_correlation(
    source_ip:  str,
    keyword:    str,
    timeframe:  int   # en secondes — vient de siem-regles.timeframe
) -> int:
    """
    Compte les événements correspondant à un pattern sur une IP
    dans une fenêtre temporelle glissante.
    Utilisée par le backend pour déclencher les règles de corrélation.

    Exemple : count_events_for_correlation("10.0.0.5", "Failed password", 60)
    → retourne 8 → le backend déclenche une alerte brute-force
    """
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