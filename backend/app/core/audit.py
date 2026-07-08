"""
Journalisation d'audit — traçabilité de toutes les actions utilisateurs.

Cahier des charges 4.7 : « Si votre SIEM lui-même est compromis, les logs
d'accès sont la seule preuve. » Chaque action sensible (connexion, échec de
connexion, création/modification/suppression d'utilisateur, de règle, de
politique de rétention, changement de statut d'alerte...) est indexée ici,
horodatée et non modifiable via l'API applicative (aucun endpoint DELETE
n'est exposé sur cet index).
"""

from datetime import datetime
from typing import Optional, Dict
import uuid
from app.core.database import es_client

INDEX_AUDIT = "smart-siem-audit"


def log_action(username: str, role: str, action: str, detail: Optional[Dict] = None, success: bool = True):
    """Enregistre une entrée d'audit. Ne doit jamais lever d'exception bloquante :
    un problème d'écriture d'audit ne doit pas empêcher l'action métier elle-même,
    mais elle est journalisée sur la sortie standard en dernier recours."""
    entry = {
        "id": f"AUD-{uuid.uuid4().hex[:10].upper()}",
        "timestamp": datetime.utcnow().isoformat(),
        "username": username or "anonyme",
        "role": role or "inconnu",
        "action": action,
        "success": success,
        "detail": detail or {},
    }
    try:
        if es_client:
            es_client.index(index=INDEX_AUDIT, id=entry["id"], document=entry)
        else:
            print(f"⚠️ [Audit] ES non connecté, entrée perdue : {entry}")
    except Exception as e:
        print(f"⚠️ [Audit] Échec d'écriture de l'entrée d'audit : {e} | {entry}")


def get_audit_log(page: int = 0, size: int = 100, username: Optional[str] = None) -> Dict:
    """Récupère le journal d'audit, du plus récent au plus ancien."""
    if not es_client:
        return {"total": 0, "entries": []}
    try:
        if not es_client.indices.exists(index=INDEX_AUDIT):
            return {"total": 0, "entries": []}

        query = {"match_all": {}}
        if username:
            query = {"term": {"username.keyword": username}}

        response = es_client.search(
            index=INDEX_AUDIT,
            query=query,
            sort=[{"timestamp": {"order": "desc"}}],
            from_=page * size,
            size=size,
        )
        entries = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]
        return {"total": total, "entries": entries}
    except Exception as e:
        print(f"⚠️ [Audit] Erreur de lecture du journal : {e}")
        return {"total": 0, "entries": []}
