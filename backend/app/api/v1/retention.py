from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Dict
from app.core.database import es_client

router = APIRouter(prefix="/api/v1/retention", tags=["Politique de Rétention des Logs"])

INDEX_CONFIG = "smart-siem-config"
CONFIG_DOC_ID = "retention_policy"
LOGS_INDEX = "smart-siem-logs"

# Unités disponibles, converties en secondes.
# 🟢 On autorise explicitement "hours" en plus des paliers réglementaires
# (30j / 6 mois / 1 an) du cahier des charges, pour permettre à l'analyste
# de tester la purge en conditions réelles (ex: 1h) sans attendre des mois.
UNIT_TO_SECONDS = {
    "hours": 3600,
    "days": 86400,
    "months": 30 * 86400,
    "years": 365 * 86400,
}

DEFAULT_POLICY = {"value": 6, "unit": "months"}  # valeur par défaut conforme au CdC (6 mois)


def _policy_to_seconds(policy: Dict) -> int:
    return int(policy["value"] * UNIT_TO_SECONDS[policy["unit"]])


def _get_policy() -> Dict:
    """Lit la politique de rétention actuellement active depuis Elasticsearch."""
    if not es_client:
        return DEFAULT_POLICY
    try:
        result = es_client.get(index=INDEX_CONFIG, id=CONFIG_DOC_ID, ignore=[404])
        if result and result.get("found"):
            src = result["_source"]
            if src.get("unit") in UNIT_TO_SECONDS and isinstance(src.get("value"), (int, float)) and src["value"] > 0:
                return {"value": src["value"], "unit": src["unit"]}
    except Exception:
        pass
    return DEFAULT_POLICY


def _save_policy(policy: Dict):
    if not es_client:
        return
    es_client.index(index=INDEX_CONFIG, id=CONFIG_DOC_ID, document=policy, refresh="wait_for")


def purge_expired_logs(policy: Optional[Dict] = None) -> int:
    """
    Supprime définitivement, dans Elasticsearch, tous les logs plus anciens
    que la politique de rétention active. Utilisée à la fois :
    - immédiatement après un changement de politique (effet instantané) ;
    - en tâche de fond périodique (voir main.py) pour rattraper les logs
      qui expirent progressivement entre deux changements de configuration.
    """
    if not es_client:
        return 0

    policy = policy or _get_policy()
    seconds = _policy_to_seconds(policy)
    cutoff = (datetime.utcnow() - timedelta(seconds=seconds)).isoformat()

    try:
        if not es_client.indices.exists(index=LOGS_INDEX):
            return 0
        result = es_client.delete_by_query(
            index=LOGS_INDEX,
            body={"query": {"range": {"timestamp": {"lt": cutoff}}}},
            refresh=True,
            conflicts="proceed",
        )
        return result.get("deleted", 0)
    except Exception as e:
        print(f"⚠️ [Rétention] Erreur lors de la purge automatique : {e}")
        return 0


@router.get("", status_code=status.HTTP_200_OK)
async def get_retention_policy():
    """Renvoie la politique de rétention actuellement appliquée par le SIEM."""
    policy = _get_policy()
    return {
        "value": policy["value"],
        "unit": policy["unit"],
        "duration_seconds": _policy_to_seconds(policy),
        "presets_reglementaires": [
            {"label": "30 jours", "value": 30, "unit": "days"},
            {"label": "6 mois", "value": 6, "unit": "months"},
            {"label": "1 an", "value": 1, "unit": "years"},
        ],
    }


@router.put("", status_code=status.HTTP_200_OK)
async def set_retention_policy(payload: Dict):
    """
    Change la politique de rétention (ex: {"value": 1, "unit": "hours"}).
    Toute valeur/unité est acceptée (1h, 30j, 6 mois, 1 an, ou une valeur
    entièrement personnalisée) pour permettre à l'analyste d'ajuster la
    conservation « à sa guise », comme l'exige la conformité RGPD du projet.
    Déclenche une purge immédiate pour un effet visible tout de suite,
    sans attendre le prochain cycle de la tâche de fond.
    """
    value = payload.get("value")
    unit = payload.get("unit")

    if not isinstance(value, (int, float)) or value <= 0:
        raise HTTPException(status_code=400, detail="Le champ 'value' doit être un nombre strictement positif.")
    if unit not in UNIT_TO_SECONDS:
        raise HTTPException(
            status_code=400,
            detail=f"Le champ 'unit' doit être l'une des valeurs suivantes : {list(UNIT_TO_SECONDS.keys())}",
        )
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")

    policy = {"value": value, "unit": unit}
    _save_policy(policy)
    deleted = purge_expired_logs(policy)

    return {
        "status": "success",
        "message": f"Politique de rétention mise à jour : {value} {unit}.",
        "policy": policy,
        "duration_seconds": _policy_to_seconds(policy),
        "logs_purges_immediatement": deleted,
    }


@router.post("/purge-now", status_code=status.HTTP_200_OK)
async def purge_now():
    """Force une purge manuelle immédiate selon la politique active (utile pour la démo/les tests)."""
    deleted = purge_expired_logs()
    policy = _get_policy()
    return {"status": "success", "logs_supprimes": deleted, "policy_appliquee": policy}
