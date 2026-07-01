import pandas as pd
from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch(["http://localhost:9200"],basic_auth=("elastic", "siem2026"))

def fetch_logs_for_export(days: int = 30, severity: str = None) -> list :
    """Récupère les logs pour export - max 10000 entrées."""
    filters = [{"range": {"timestamp": {"gte": f"now-{days}d"}}}]
    if severity:
        filters.append({"term": {"severity": severity}})

    result = es.search(index="siem-logs", body={"query": {"bool": {"must": filters}},
                                                "sort": [{"timestamp": {"order": "desc"}}],
                                                "size": 10000})
    return [hit["_source"] for hit in result["hits"]["hits"]]

def export_csv(days: int = 30, severity: str = None) -> str:
    """Export CSV pour audit externe."""
    logs = fetch_logs_for_export(days, severity)
    df = pd.DataFrame(logs)
    filename = f"export_siem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"CSV exporté : {filename}")
    return filename

def export_excel(days: int = 30) -> str:
    """Export Excel multi-onglets pour auditeur."""
    filename = f"export_siem_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

    # Onglet 1 — tous les logs
    logs_df = pd.DataFrame(fetch_logs_for_export(days))

    # Onglet 2 — uniquement les critiques
    critical_df = pd.DataFrame(fetch_logs_for_export(days, severity="critical"))

    # Onglet 3 — uniquement les suspects
    result = es.search(index="siem-logs", body={
        "query": {"bool": {"must": [
            {"term":  {"is_suspect": True}},
            {"range": {"timestamp": {"gte": f"now-{days}d"}}}
        ]}},
        "size": 10000
    })
    suspects_df = pd.DataFrame([h["_source"] for h in result["hits"]["hits"]])

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        logs_df.to_excel(     writer, sheet_name="Tous les logs",   index=False)
        critical_df.to_excel( writer, sheet_name="Critiques",       index=False)
        if not suspects_df.empty:
            suspects_df.to_excel(writer, sheet_name="Suspects",     index=False)

    print(f"✅ Excel exporté : {filename}")
    return filename