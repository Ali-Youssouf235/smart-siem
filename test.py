# data/tests.py
import os, sys

print("=" * 50)
print("TESTS COUCHE DATA — Smart SIEM")
print("=" * 50)

erreurs = []

def ok(msg):    print(f"  ✅ {msg}")
def fail(msg):  print(f"  ❌ {msg}"); erreurs.append(msg)

# ── Connexion ──────────────────────────────────
print("\n[1] Connexion Elasticsearch")
try:
    from elasticsearch import Elasticsearch
    es = Elasticsearch(["http://localhost:9200"], basic_auth=("elastic", "siem2026"))
    es.info()
    ok("Connexion réussie")
except Exception as e:
    fail(f"Connexion échouée : {e}")

# ── Index ──────────────────────────────────────
print("\n[2] Vérification des 8 index")
try:
    attendus = ['siem-logs','siem-alertes','siem-utilisateurs','siem-regles',
                'siem-perimetres','siem-actions-incidents','siem-audit','siem-ueba']
    existants = [i['index'] for i in es.cat.indices(format='json')]
    for a in attendus:
        if a in existants: ok(a)
        else:              fail(f"{a} manquant")
except Exception as e:
    fail(f"Erreur vérification index : {e}")

# ── Pipeline ───────────────────────────────────
print("\n[3] Pipeline d'ingestion")
try:
    from pipeline import ingest_log
    doc = ingest_log("Failed password for root from 10.0.0.5 port 22", "srv-test")
    assert doc['log_type'] == 'auth'
    assert doc['severity'] == 'critical'
    assert doc['source_ip'] == '10.0.0.5'
    ok("ingest_log() fonctionne")
except Exception as e:
    fail(f"ingest_log() : {e}")

# ── Recherche ──────────────────────────────────
print("\n[4] Moteur de recherche")
try:
    from search import search_logs, get_timeline, count_events_for_correlation, mark_suspect
    r = search_logs(size=5)
    assert 'total' in r and 'logs' in r
    ok(f"search_logs() — {r['total']} logs")

    tl = get_timeline(host='srv-test')
    assert 'timeline' in tl
    ok("get_timeline() fonctionne")

    count = count_events_for_correlation('10.0.0.5', 'Failed password', 3600)
    assert isinstance(count, int)
    ok(f"count_events_for_correlation() — {count} événements")
except Exception as e:
    fail(f"Recherche : {e}")

# ── Exports ────────────────────────────────────
print("\n[5] Exports")
try:
    from export import export_csv, export_excel
    f = export_csv(days=30);  assert os.path.exists(f); os.remove(f); ok("export_csv() OK")
    f = export_excel(days=30); assert os.path.exists(f); os.remove(f); ok("export_excel() OK")
except Exception as e:
    fail(f"Export : {e}")

# ── PDF ────────────────────────────────────────
print("\n[6] Rapport PDF")
try:
    from report_generator import generate_pdf_report
    f = "test.pdf"
    generate_pdf_report(days=7, output=f)
    assert os.path.exists(f); os.remove(f); ok("generate_pdf_report() OK")
except Exception as e:
    fail(f"PDF : {e}")

# ── Résultat final ─────────────────────────────
print("\n" + "=" * 50)
if erreurs:
    print(f"❌ {len(erreurs)} erreur(s) détectée(s) :")
    for e in erreurs: print(f"   - {e}")
    sys.exit(1)
else:
    print("✅ Tous les tests passent — prêt à merger sur main !")
print("=" * 50)