# test_rbac.py
import requests
from requests.auth import HTTPBasicAuth

BASE = "http://localhost:9200"

# ── Utilitaires ───────────────────────────────────────

def test(description, condition):
    status = "✅" if condition else "❌"
    print(f"  {status} {description}")
    return condition

def get(url, auth):
    try:
        r = requests.get(f"{BASE}{url}", auth=auth)
        return r.status_code, r.json()
    except Exception as e:
        return 0, str(e)

def put(url, auth, body={}):
    try:
        r = requests.put(f"{BASE}{url}", json=body, auth=auth)
        return r.status_code, r.json()
    except Exception as e:
        return 0, str(e)

def delete(url, auth):
    try:
        r = requests.delete(f"{BASE}{url}", auth=auth)
        return r.status_code, r.json()
    except Exception as e:
        return 0, str(e)

# ── Credentials par rôle ──────────────────────────────

LECTEUR  = HTTPBasicAuth("lecteur_test1",  "Lecteur2026!")
ANALYSTE = HTTPBasicAuth("analyste_test1", "Analyste2026!")
ADMIN    = HTTPBasicAuth("admin_test1",    "Admin2026!")
ELASTIC  = HTTPBasicAuth("elastic",       "siem2026")

erreurs = []

# ═════════════════════════════════════════════════════
# TEST 1 — LECTEUR
# Peut : lire siem-logs et siem-alertes
# Ne peut pas : écrire, accéder aux autres index
# ═════════════════════════════════════════════════════
print("\n[1] Rôle LECTEUR")

code, _ = get("/siem-logs/_search", LECTEUR)
ok = test("Peut lire siem-logs", code == 200)
if not ok: erreurs.append("Lecteur ne peut pas lire siem-logs")

code, _ = get("/siem-alertes/_search", LECTEUR)
ok = test("Peut lire siem-alertes", code == 200)
if not ok: erreurs.append("Lecteur ne peut pas lire siem-alertes")

code, _ = put("/siem-logs/_doc/test-lecteur", LECTEUR, {"test": "data"})
ok = test("Ne peut PAS écrire dans siem-logs", code == 403)
if not ok: erreurs.append("Lecteur peut écrire dans siem-logs — PROBLÈME SÉCURITÉ")

code, _ = get("/siem-utilisateurs/_search", LECTEUR)
ok = test("Ne peut PAS accéder à siem-utilisateurs", code == 403)
if not ok: erreurs.append("Lecteur accède à siem-utilisateurs — PROBLÈME SÉCURITÉ")

code, _ = get("/siem-audit/_search", LECTEUR)
ok = test("Ne peut PAS accéder à siem-audit", code == 403)
if not ok: erreurs.append("Lecteur accède à siem-audit — PROBLÈME SÉCURITÉ")

# ═════════════════════════════════════════════════════
# TEST 2 — ANALYSTE
# Peut : lire + écrire siem-logs, siem-alertes, siem-audit
# Ne peut pas : accéder à siem-utilisateurs, supprimer
# ═════════════════════════════════════════════════════
print("\n[2] Rôle ANALYSTE")

code, _ = get("/siem-logs/_search", ANALYSTE)
ok = test("Peut lire siem-logs", code == 200)
if not ok: erreurs.append("Analyste ne peut pas lire siem-logs")

code, _ = put("/siem-logs/_doc/test-analyste", ANALYSTE, {
    "timestamp":   "2026-06-22T03:14:22Z",
    "raw_message": "test rbac analyste",
    "host":        "test",
    "log_type":    "auth",
    "severity":    "info",
    "is_suspect":  False,
    "perimetre_id":"perimetre-dmz"
})
ok = test("Peut écrire dans siem-logs", code in [200, 201])
if not ok: erreurs.append("Analyste ne peut pas écrire dans siem-logs")

code, _ = get("/siem-audit/_search", ANALYSTE)
ok = test("Peut lire siem-audit", code == 200)
if not ok: erreurs.append("Analyste ne peut pas lire siem-audit")

code, _ = get("/siem-utilisateurs/_search", ANALYSTE)
ok = test("Ne peut PAS accéder à siem-utilisateurs", code == 403)
if not ok: erreurs.append("Analyste accède à siem-utilisateurs — PROBLÈME SÉCURITÉ")

code, _ = delete("/siem-logs/_doc/test-analyste", ANALYSTE)
ok = test("Ne peut PAS supprimer dans siem-logs", code == 403)
if not ok: erreurs.append("Analyste peut supprimer — PROBLÈME SÉCURITÉ")

# ═════════════════════════════════════════════════════
# TEST 3 — ADMIN
# Peut : tout sur tous les index siem-*
# ═════════════════════════════════════════════════════
print("\n[3] Rôle ADMIN")

for index in ["siem-logs", "siem-alertes", "siem-utilisateurs",
              "siem-regles", "siem-audit", "siem-ueba"]:
    code, _ = get(f"/{index}/_search", ADMIN)
    ok = test(f"Peut lire {index}", code == 200)
    if not ok: erreurs.append(f"Admin ne peut pas lire {index}")

code, _ = put("/siem-logs/_doc/test-admin", ADMIN, {
    "timestamp":   "2026-06-22T03:14:22Z",
    "raw_message": "test rbac admin",
    "host":        "test",
    "log_type":    "auth",
    "severity":    "info",
    "is_suspect":  False,
    "perimetre_id":"perimetre-dmz"
})
ok = test("Peut écrire dans siem-logs", code in [200, 201])
if not ok: erreurs.append("Admin ne peut pas écrire")

code, _ = delete("/siem-logs/_doc/test-admin", ADMIN)
ok = test("Peut supprimer dans siem-logs", code == 200)
if not ok: erreurs.append("Admin ne peut pas supprimer")

# Nettoyer le doc de test de l'analyste
delete("/siem-logs/_doc/test-analyste", ELASTIC)

# ═════════════════════════════════════════════════════
# RÉSULTAT FINAL
# ═════════════════════════════════════════════════════
print("\n" + "=" * 50)
if erreurs:
    print(f"❌ {len(erreurs)} problème(s) détecté(s) :")
    for e in erreurs:
        print(f"   - {e}")
else:
    print("✅ RBAC entièrement validé — tous les rôles fonctionnent correctement")
print("=" * 50)