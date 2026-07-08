from fpdf import FPDF
from datetime import datetime
import tempfile
import os
import base64
import uuid
from app.core.database import es_client
from typing import Dict, Any, List

INDEX_REPORTS_ARCHIVE = "smart-siem-reports-archive"

class SIEMReportPDF(FPDF):
    def header(self):
        # Design En-tête Pro (Tiret simple "-" validé pour la police)
        self.set_fill_color(31, 41, 55) # Gris très foncé/Bleu nuit
        self.rect(0, 0, 210, 35, "F")
        
        self.set_font("Arial", "B", 18)
        self.set_text_color(255, 255, 255)
        self.text(15, 15, "SMART SIEM - REPORTING & AUDIT AUTOMATISE")
        
        self.set_font("Arial", "I", 9)
        self.set_text_color(209, 213, 219)
        date_str = datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S UTC")
        self.text(15, 23, f"Genere le : {date_str} | Classification : CONFIDENTIEL SOC")
        self.ln(30)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(156, 163, 175)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Smart SIEM Security Analytics", border=0, align="C")

def fetch_advanced_siem_stats() -> Dict[str, Any]:
    """Extrait des statistiques ultra-détaillées via les agrégations Elasticsearch"""
    stats = {
        "total_logs": 0, "total_alerts": 0,
        "severities": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
        "top_hosts": [], "top_attackers": []
    }
    if not es_client:
        return stats
        
    try:
        # 1. Volumétrie de base
        stats["total_logs"] = es_client.count(index="smart-siem-logs", body={"query": {"match_all": {}}})["count"]
        
        # 2. Extraction et comptage des alertes uniquement
        alert_query = {"query": {"prefix": {"id.keyword": "ALT-"}}}
        stats["total_alerts"] = es_client.count(index="smart-siem-logs", body=alert_query)["count"]

        # 3. Agrégation par niveau de criticité pour les alertes
        severity_agg = {
            "query": {"prefix": {"id.keyword": "ALT-"}},
            "aggs": {"by_severity": {"terms": {"field": "niveau_criticite.keyword"}}}
        }
        res_sev = es_client.search(index="smart-siem-logs", body=severity_agg, size=0)
        for buckets in res_sev["aggregations"]["by_severity"]["buckets"]:
            stats["severities"][buckets["key"]] = buckets["doc_count"]

        # 4. Top 3 Hôtes les plus visés (Agrégation)
        host_agg = {
            "aggs": {"by_host": {"terms": {"field": "host.keyword", "size": 3}}}
        }
        res_host = es_client.search(index="smart-siem-logs", body=host_agg, size=0)
        stats["top_hosts"] = [
            {"name": b["key"], "count": b["doc_count"]} 
            for b in res_host["aggregations"]["by_host"]["buckets"]
        ]

        # 5. Top 3 IP Sources suspectes (uniquement sur les logs d'échec d'authentification)
        attacker_agg = {
            "query": {"term": {"log_type.keyword": "auth"}},
            "aggs": {"by_ip": {"terms": {"field": "source_ip.keyword", "size": 3}}}
        }
        res_attack = es_client.search(index="smart-siem-logs", body=attacker_agg, size=0)
        stats["top_attackers"] = [
            {"ip": b["key"], "count": b["doc_count"]} 
            for b in res_attack["aggregations"]["by_ip"]["buckets"]
        ]

    except Exception as e:
        print(f"[!] Erreur extraction agrégations : {str(e)}")
        
    return stats

def generate_security_pdf() -> str:
    """Génère un rapport de sécurité enrichi et détaillé"""
    data = fetch_advanced_siem_stats()
    
    pdf = SIEMReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.ln(5)
    
    # ─── SECTION 1 : INDICES DE VOLUMÉTRIE ───
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, "1. KPIs de Volumetrie Globale", ln=1)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(55, 65, 81)
    pdf.cell(95, 8, f" Total des evenements indexes : {data['total_logs']}", border=1)
    pdf.cell(95, 8, f" Total des alertes de securite : {data['total_alerts']}", border=1, ln=1)
    pdf.ln(5)
    
    # ─── SECTION 2 : TABLEAU DES SÉVÉRITÉS ───
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, "2. Classification des Alertes par Niveau de Severite", ln=1)
    
    # En-tête Tableau
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(229, 231, 235)
    pdf.cell(95, 8, "Niveau de Criticite", border=1, fill=True)
    pdf.cell(95, 8, "Nombre d'incidents detectes", border=1, ln=1, fill=True)
    
    # Données Tableau
    pdf.set_font("Arial", "", 10)
    for sev, count in data["severities"].items():
        pdf.cell(95, 8, f" {sev}", border=1)
        pdf.cell(95, 8, f" {count} alerte(s)", border=1, ln=1)
    pdf.ln(5)
    
    # ─── SECTION 3 : TOP MENACES & CIBLES ───
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, "3. Top 3 des Entites Cibles et Sources de Menaces", ln=1)
    
    # Colonne 1 : Hôtes Visés
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 8, "Machines (Hosts) les plus sollicitees", ln=0)
    pdf.cell(95, 8, "IP Sources les plus actives (Auth)", ln=1)
    
    pdf.set_font("Arial", "", 10)
    # Alignement des tops côte à côte
    for i in range(3):
        # Bloc Hôte
        if i < len(data["top_hosts"]):
            h = data["top_hosts"][i]
            host_text = f"  {i+1}. {h['name']} ({h['count']} logs)"
        else:
            host_text = "  ---"
        pdf.cell(95, 8, host_text, border="B")
        
        # Bloc Attaquant
        if i < len(data["top_attackers"]):
            a = data["top_attackers"][i]
            attack_text = f"  {i+1}. {a['ip']} ({a['count']} tentatives)"
        else:
            attack_text = "  ---"
        pdf.cell(95, 8, attack_text, border="B", ln=1)
        
    pdf.ln(8)
    
    # ─── SECTION 4 : STRATÉGIE DE REMÉDIATION SOAR ───
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, "4. Rapport d'Action de Mitigation (SOAR)", ln=1)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(55, 65, 81)
    pdf.multi_cell(0, 6, "Analyse : Le volume d'incidents critiques genere automatiquement des regles de pare-feu restrictives. Les IP listees dans la section 3 ayant un taux d'echecs eleve ont ete transmises au module de bannissement IP. Recommandation : Mettre en place un second facteur d'authentification (MFA) sur les serveurs les plus cibles.")
    
    # Sauvegarde universelle
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, "smart_siem_report.pdf")
    pdf.output(file_path)
    
    return file_path


def archive_generated_report(pdf_path: str, report_type: str = "manuel") -> Dict[str, Any]:
    """
    Archive une copie du PDF généré (base64) dans Elasticsearch, pour
    alimenter un véritable "Historique des livrables" côté Frontend
    (exigence 4.5 : rapports consultables après coup, pas seulement
    téléchargés une fois puis perdus).
    """
    if not es_client:
        return {}

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    doc = {
        "generated_at": datetime.utcnow().isoformat(),
        "type": report_type,  # "manuel" | "auto_quotidien" | "auto_hebdomadaire"
        "filename": f"smart_siem_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf",
        "size_bytes": len(pdf_bytes),
        "pdf_base64": base64.b64encode(pdf_bytes).decode("utf-8"),
    }
    doc_id = str(uuid.uuid4())
    es_client.index(index=INDEX_REPORTS_ARCHIVE, id=doc_id, document=doc, refresh="wait_for")
    doc["id"] = doc_id
    doc.pop("pdf_base64")  # on ne renvoie pas le binaire dans les métadonnées
    return doc


def generate_and_archive_report(report_type: str = "manuel") -> Dict[str, Any]:
    """Raccourci : génère le PDF puis l'archive immédiatement."""
    pdf_path = generate_security_pdf()
    return archive_generated_report(pdf_path, report_type=report_type)