from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"],
                   basic_auth=("elastic", "siem2026"))
styles= getSampleStyleSheet()

def fetch_report_data(days: int=7) -> dict:
    """Récupère toutes les stats nécessaires pour le rapport."""
    since = f"now-{days}d"

    total = es.count(index="siem-logs", body={
        "query": {"range": {"timestamp": {"gte": since}}},
        "aggs": {"by_severity": {"terms": {"field": "severity"}}}
    })
    severity_agg = es.search(index="siem-logs", body={
        "size": 0,
        "query": {"range": {"timestamp": {"gte": since}}},
        "aggs": {"by_severity": {"terms": {"field": "severity"}}}
    })

    severity = {
        b["key"]: b["doc_count"]
        for b in severity_agg["aggretions"]["by_severity"]["buckets"]
    }

    ip_agg = es.search(index="siem-logs", body={
        "size": 0,
        "query": {"range": {"timestamp": {"gte": since}}},
        "aggs": {"top_ips": {"terms": {"field": "source_ip", "size": 5}}}
    })

    top_ips = [
        (b["key"], b["doc_count"])
        for b in ip_agg["aggretions"]["top_ips"]["buckets"]
    ]

    alertes = es.count(index="siem-alertes", body={
        "query": {"range": {"timestamp": {"gte": since}}}
    })["count"]


    suspects = es.count(index="siem-logs", body={
        "query": {
            "bool": {
                "must": [
                    {"test": {"is_suspect": True}},
                    {"range": {"timestamp": {"gte": since}}}
                ]
            }
        }
    })["count"]

    return {
        "total": total,
        "severity": severity,
        "top_ips": top_ips,
        "alertes": alertes,
        "suspects": suspects
    }

def generate_pdf_report(days: int = 7, output: str = "rapport_siem.pdf"):
    """Génère le rapport PDF automatiquement."""
    data = fetch_report_data(days)
    doc  = SimpleDocTemplate(output, pagesize=A4)
    story = []

    # En-tête
    story.append(Paragraph(f"Rapport de sécurité SIEM — {days} derniers jours", styles["Title"]))
    story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 20))

    # Résumé
    story.append(Paragraph("Résumé", styles["Heading2"]))
    summary = [
        ["Indicateur",              "Valeur"],
        ["Total événements",        str(data["total"])],
        ["Alertes déclenchées",     str(data["alertes"])],
        ["Logs suspects",           str(data["suspects"])],
        ["Événements critiques",    str(data["severity"].get("critical", 0))],
        ["Événements warning",      str(data["severity"].get("warning",  0))],
        ["Événements info",         str(data["severity"].get("info",     0))],
    ]
    t = Table(summary, colWidths=[300, 150])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1D9E75")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F1EFE8")]),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#B4B2A9")),
        ("PADDING",    (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # Top 5 IPs
    story.append(Paragraph("Top 5 adresses IP", styles["Heading2"]))
    ip_data = [["Adresse IP", "Nombre d'événements"]] + [
        [ip, str(count)] for ip, count in data["top_ips"]
    ]
    t2 = Table(ip_data, colWidths=[300, 150])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#534AB7")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#EEEDFE")]),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#B4B2A9")),
        ("PADDING",    (0,0), (-1,-1), 8),
    ]))
    story.append(t2)

    doc.build(story)
    print(f"✅ Rapport généré : {output}")

if __name__ == "__main__":
    generate_pdf_report(days=7)