import requests
from requests.auth import HTTPBasicAuth

BASE = "http://localhost:9200"
AUTH = HTTPBasicAuth("elastic", "siem2026")

def create_retention_policy() :

    policy = {
        "policy": {
            "phases": {
                "hot": {
                    "min_age": "0ms",
                    "actions": {}
                },
                "delete": {
                    "min_age": "30d",
                    "actions": {
                        "delete": {}
                    }
                }
            }
        }
    }

    r = requests.put(
        f"{BASE}/_ilm/policy/siem-logs-policy",
        json=policy,
        auth=AUTH
    )
    print(f"Ilm policy created : {r.status_code} {r.text}")

    r = requests.put(
        f"{BASE}/siem-logs/_settings",
        json={"index.lifecycle.name": "siem-logs-policy"},
        auth=AUTH
    )
    print(f"Index settings updated : {r.status_code} {r.text}")

create_retention_policy()