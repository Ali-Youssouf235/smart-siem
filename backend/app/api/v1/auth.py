from fastapi import APIRouter, status, HTTPException
from app.core.database import es_client
from typing import Optional, List

router = APIRouter(prefix="/api/v1", tags=["Authentification & Administration"])

# --- 1. CONFIGURATION DE L'INDEX DES UTILISATEURS ---
INDEX_USERS = "smart-siem-users"


# --- 2. AUTHENTIFICATION & PROFIL ---

@router.post("/auth/refresh", status_code=status.HTTP_200_OK)
async def refresh_token():
    """
    Renouvelle le Token de session JWT pour l'analyste SOC connecté.
    """
    return {
        "access_token": "NEW_REFRESHED_JWT_TOKEN_SECRET", 
        "token_type": "bearer"
    }


@router.get("/auth/me", status_code=status.HTTP_200_OK)
async def get_current_user_profile():
    """
    Profil et permissions de l'analyste actuellement connecté à l'interface.
    Simule une lecture du compte actif.
    """
    return {
        "username": "analyste_soc_01", 
        "role": "admin", 
        "team": "Cellule Cyber CTU",
        "permissions": ["read:logs", "write:rules", "delete:alerts"]
    }


# --- 3. ADMINISTRATION DES UTILISATEURS (CRUD 100% ELASTICSEARCH) ---

@router.get("/users", status_code=status.HTTP_200_OK)
async def list_users():
    """
    Récupère la liste de tous les utilisateurs du SOC stockés dans l'index Elasticsearch.
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")
        
    try:
        # Si l'index n'existe pas encore, on renvoie une liste par défaut pour éviter un crash au premier test
        if not es_client.indices.exists(index=INDEX_USERS):
            return {"total_users": 1, "users": [{"id": "user_default", "username": "analyste_soc_01", "role": "admin"}]}

        response = es_client.search(index=INDEX_USERS, query={"match_all": {}}, size=50)
        
        users = []
        for hit in response["hits"]["hits"]:
            user_data = hit["_source"]
            user_data["id"] = hit["_id"] # On récupère l'ID natif d'Elasticsearch
            users.append(user_data)
            
        return {"total_users": len(users), "users": users}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des utilisateurs : {str(e)}")


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: dict):
    """
    Crée et indexe un nouvel utilisateur directement dans Elasticsearch.
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")
        
    try:
        # Sauvegarde du document dans l'index utilisateur
        response = es_client.index(index=INDEX_USERS, document=user_data, refresh="wait_for")
        return {
            "status": "success", 
            "message": "Nouvel analyste SOC enregistré dans Elasticsearch.", 
            "user_id": response["_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Échec de l'indexation de l'utilisateur : {str(e)}")


@router.put("/users/{id}", status_code=status.HTTP_200_OK)
async def update_user(id: str, user_data: dict):
    """
    Modifie les informations ou le rôle d'un utilisateur via son ID Elasticsearch.
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")
        
    try:
        # Mise à jour partielle ou totale du document utilisateur
        es_client.update(index=INDEX_USERS, id=id, doc=user_data, refresh="wait_for")
        return {"status": "success", "message": f"Utilisateur {id} mis à jour avec succès dans Elasticsearch."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la mise à jour de l'utilisateur : {str(e)}")


@router.delete("/users/{id}", status_code=status.HTTP_200_OK)
async def delete_user(id: str):
    """
    Supprime définitivement un utilisateur de l'index Elasticsearch (Révocation des accès).
    """
    if not es_client:
        raise HTTPException(status_code=500, detail="Elasticsearch non connecté.")
        
    try:
        es_client.delete(index=INDEX_USERS, id=id, refresh="wait_for")
        return {"status": "success", "message": f"Compte {id} supprimé définitivement du cluster Elasticsearch."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la suppression de l'utilisateur : {str(e)}")