from fastapi import APIRouter, status, HTTPException
from app.core.database import es_client
from typing import List, Dict, Optional

router = APIRouter(prefix="/api/v1/rules", tags=["Gestion des Règles de Détection"])

INDEX_RULES = "smart-siem-rules"

# Règles injectées une seule fois, à la création de l'index (première utilisation),
# pour ne jamais repartir d'une base vide. Au-delà de cette initialisation,
# TOUT passe réellement par Elasticsearch : plus aucune donnée en mémoire.
DEFAULT_RULES = [
    {
        "id": "S3",
        "name": "SSH Brute-Force Detection",
        "description": "Détecte les tentatives répétées d'échecs d'authentification SSH.",
        "enabled": True,
        "threshold": 5,
        "severity": "CRITICAL",
    },
    {
        "id": "S4",
        "name": "UEBA - Behavioral Anomaly",
        "description": "Détection d'anomalies comportementales (connexions hors-horaires, comptes inhabituels).",
        "enabled": True,
        "threshold": None,
        "severity": "CRITICAL",
    },
    {
        "id": "S6",
        "name": "Lateral Movement Detection",
        "description": "Surveillance des rebonds suspects vers des infrastructures critiques (ex: DC Server).",
        "enabled": True,
        "threshold": 3,
        "severity": "HIGH",
    },
]


def _ensure_index_seeded():
    """Crée l'index et y insère les règles par défaut s'il n'existe pas encore."""
    if not es_client:
        return
    if es_client.indices.exists(index=INDEX_RULES):
        return
    for rule in DEFAULT_RULES:
        es_client.index(index=INDEX_RULES, id=rule["id"], document=rule, refresh="wait_for")


# --- 1. LISTER LES RÈGLES ---
@router.get("", status_code=status.HTTP_200_OK)
async def list_rules():
    """
    Récupère la liste réelle de toutes les règles de corrélation stockées
    dans Elasticsearch (index smart-siem-rules).
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")

    try:
        _ensure_index_seeded()
        response = es_client.search(index=INDEX_RULES, query={"match_all": {}}, size=100)

        rules = []
        for hit in response["hits"]["hits"]:
            rule_data = hit["_source"]
            rule_data["id"] = hit["_id"]  # L'ID Elasticsearch fait foi
            rules.append(rule_data)

        return {"total_rules": len(rules), "rules": rules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des règles : {str(e)}")


# --- 2. CRÉER UNE RÈGLE ---
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_rule(rule_data: dict):
    """
    Crée et indexe réellement une nouvelle règle de corrélation dans Elasticsearch.
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")

    try:
        _ensure_index_seeded()
        custom_id = rule_data.pop("id", None)  # évite de dupliquer l'id dans le _source

        if custom_id:
            response = es_client.index(
                index=INDEX_RULES, id=custom_id, document=rule_data, refresh="wait_for"
            )
            new_id = response["_id"]
        else:
            response = es_client.index(index=INDEX_RULES, document=rule_data, refresh="wait_for")
            new_id = response["_id"]

        return {
            "status": "success",
            "message": f"Nouvelle règle de sécurité {new_id} enregistrée avec succès dans Elasticsearch.",
            "rule": {"id": new_id, **rule_data},
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Échec de la création de la règle : {str(e)}")


# --- 3. MODIFIER UNE RÈGLE ---
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_rule(id: str, rule_data: dict):
    """
    Modifie réellement, dans Elasticsearch, les critères ou le seuil d'une
    règle existante (ex: changer le seuil d'échecs SSH de la règle S3).
    Cette modification est immédiatement prise en compte par le moteur de
    corrélation (voir app/core/engine.py -> get_rule_config), sans redémarrage.
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")

    try:
        if not es_client.exists(index=INDEX_RULES, id=id):
            raise HTTPException(status_code=404, detail=f"La règle {id} n'existe pas.")

        es_client.update(index=INDEX_RULES, id=id, doc=rule_data, refresh="wait_for")

        return {
            "status": "success",
            "message": f"Règle {id} mise à jour et rechargée dans le moteur de corrélation.",
            "updated_fields": rule_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- 4. SUPPRIMER UNE RÈGLE ---
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_rule(id: str):
    """
    Supprime définitivement une règle du moteur de détection dans Elasticsearch.
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")

    try:
        if not es_client.exists(index=INDEX_RULES, id=id):
            raise HTTPException(status_code=404, detail=f"La règle {id} n'existe pas.")

        es_client.delete(index=INDEX_RULES, id=id, refresh="wait_for")

        return {
            "status": "success",
            "message": f"Règle {id} supprimée définitivement du cluster Elasticsearch.",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))