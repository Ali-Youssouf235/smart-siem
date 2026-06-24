# setup_indices.py
import requests, json

ELASTIC_PASSWORD = "siem2026"
BASE = "http://localhost:9200"

session = requests.Session()
session.auth = ("elastic", ELASTIC_PASSWORD)
session.verify = False

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_index(name, mapping):
    r = session.put(f"{BASE}/{name}", json=mapping)
    status = "OK" if r.status_code in [200, 400] else "ERREUR"
    print(f"[{status}] Index '{name}' : {r.json().get('acknowledged', r.text)}")

# ─────────────────────────────────────────
# INDEX 1 : logs  (table principale — la plus importante)
# ─────────────────────────────────────────
create_index("siem-logs", {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        # Politique de rétention ILM (Index Lifecycle Management)
        "index.lifecycle.name": "siem-logs-policy"
    },
    "mappings": {
        "properties": {
            "id":             {"type": "keyword"},        # UUID exact
            "timestamp":      {"type": "date"},           # indexé, trié
            "source_ip":      {"type": "ip"},             # supporte IPv4/IPv6
            "destination_ip": {"type": "ip"},
            "host":           {"type": "keyword"},
            "log_type":       {"type": "keyword"},        # 'auth','réseau','système','application'
            "severity":       {"type": "keyword"},        # 'info','warning','critical'
            "raw_message":    {"type": "text",            # recherche fulltext
                               "fields": {"keyword": {"type": "keyword"}}},
            "is_suspect":     {"type": "boolean"},
            "perimetre_id":   {"type": "keyword"}
        }
    }
})

# ─────────────────────────────────────────
# INDEX 2 : perimetres_securite
# ─────────────────────────────────────────
create_index("siem-perimetres", {
    "mappings": {
        "properties": {
            "id":              {"type": "keyword"},
            "nom_perimetre":   {"type": "keyword"},
            "type_perimetre":  {"type": "keyword"}    # 'équipe','service','filiale','environnement'
        }
    }
})

# ─────────────────────────────────────────
# INDEX 3 : utilisateurs (RBAC)
# ─────────────────────────────────────────
create_index("siem-utilisateurs", {
    "mappings": {
        "properties": {
            "id":            {"type": "keyword"},
            "username":      {"type": "keyword"},
            "password_hash": {"type": "keyword", "index": False},  # jamais cherché
            "role":          {"type": "keyword"},   # 'Lecteur','Analyste','Administrateur'
            "perimetre_id":  {"type": "keyword"}
        }
    }
})

# ─────────────────────────────────────────
# INDEX 4 : regles_correlation
# ─────────────────────────────────────────
create_index("siem-regles", {
    "mappings": {
        "properties": {
            "id":             {"type": "keyword"},
            "nom":            {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "description":    {"type": "text"},
            "mitre_category": {"type": "keyword"},  # 'reconnaissance','mouvement latéral'...
            "threshold":      {"type": "integer"},
            "timeframe":      {"type": "integer"}   # en secondes
        }
    }
})

# ─────────────────────────────────────────
# INDEX 5 : alertes
# ─────────────────────────────────────────
create_index("siem-alertes", {
    "mappings": {
        "properties": {
            "id":               {"type": "keyword"},
            "timestamp":        {"type": "date"},
            "niveau_criticite": {"type": "keyword"},  # 'INFO','WARNING','HIGH','CRITICAL'
            "statut":           {"type": "keyword"},  # 'ouvert','en cours','résolu'
            "regle_id":         {"type": "keyword"},
            "utilisateur_id":   {"type": "keyword"}
        }
    }
})

# ─────────────────────────────────────────
# INDEX 6 : logs_actions_incidents (SOAR)
# ─────────────────────────────────────────
create_index("siem-actions-incidents", {
    "mappings": {
        "properties": {
            "id":          {"type": "keyword"},
            "action_type": {"type": "keyword"},  # 'blocage_ip','desactivation_compte'...
            "timestamp":   {"type": "date"},
            "description": {"type": "text"},
            "alerte_id":   {"type": "keyword"}
        }
    }
})

# ─────────────────────────────────────────
# INDEX 7 : logs_actions_utilisateurs (audit)
# ─────────────────────────────────────────
create_index("siem-audit", {
    "mappings": {
        "properties": {
            "id":             {"type": "keyword"},
            "action_type":    {"type": "keyword"},
            "timestamp":      {"type": "date"},
            "utilisateur_id": {"type": "keyword"}
        }
    }
})

# ─────────────────────────────────────────
# INDEX 8 : profils_comportementaux_ueba
# ─────────────────────────────────────────
create_index("siem-ueba", {
    "mappings": {
        "properties": {
            "id":                    {"type": "keyword"},
            "entite_type":           {"type": "keyword"},   # 'utilisateur' ou 'machine'
            "entite_identifiant":    {"type": "keyword"},
            "horaires_habituels":    {"type": "keyword"},
            "volume_moyen_data":     {"type": "integer"},
            "score_risque_dynamique":{"type": "float"}
        }
    }
})

print("\n✅ Tous les index sont créés !")