import requests
from requests.auth import HTTPBasicAuth

BASE = "http://localhost:9200"
AUTH = HTTPBasicAuth("elastic", "siem2026")


roles = {
    "siem_lecteur": {
        "indices": [
            {
                "names": ["siem-logs", "siem-alertes"],
                "privileges": ["read"]
            }
        ],
        "applications": [{
            "application": "kibana-.kibana",
            "privileges": ["feature_discover.read",  # peut chercher des logs
                           "feature_dashboard.read"],  # peut voir les dashboards
            "resources": ["*"]
        }]
    },

    "siem_analyste": {
        "indices": [{
            "names": ["siem-logs", "siem-alertes"],
            "privileges": ["read", "write"]
        }],
        "applications": [{
            "application": "kibana-.kibana",
            "privileges": ["feature_discover.all",  # peut chercher et filtrer
                           "feature_dashboard.all",  # peut voir et modifier
                           "feature_dev_tools.all"],  # peut utiliser Dev Tools
            "resources": ["*"]
        }]
    },

    "siem_admin": {
        "indices": [{
            "names": ["siem-*"],
            "privileges": ["all"]
        }],
        "applications": [{
            "application": "kibana-.kibana",
            "privileges": ["all"],  # accès total à Kibana
            "resources": ["*"]
        }]
    }
}

for nom, config in roles.items():
    r = requests.put(
        f"{BASE}/_security/role/{nom}",
        json=config,
        auth=AUTH,
    )
    print(f"Rôle {nom} : {r.json()}")

utilisateurs = [
    {
        "username": "lecteur_test1",
        "password": "Lecteur2026!",
        "role":    ["siem_lecteur"],
        "full_name":"Lecteur Test"
    },
    {
        "username": "analyste_test1",
        "password": "Analyste2026!",
        "role":    ["siem_analyste"],
        "full_name":"Analyste Test"
    },
    {
        "username": "admin_test1",
        "password": "Admin2026!",
        "role":    ["siem_admin"],
        "full_name":"Admin Test"
    }
]

for u in utilisateurs:
    r = requests.put(
        f"{BASE}/_security/user/{u['username']}",
        json={
            "password":  u["password"],
            "roles":     u["role"],
            "full_name": u["full_name"]
        },
        auth=AUTH
    )
    print(f"Utilisateur '{u['username']}' : {r.json()}")

print("\n✅ RBAC configuré !")