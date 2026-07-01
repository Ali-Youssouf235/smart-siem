from fastapi import APIRouter, status, HTTPException
from typing import List, Dict

router = APIRouter(prefix="/api/v1/rules", tags=["Gestion des Règles de Détection"])

# Simulation d'une base de données en mémoire pour les tests avant branchement ES/DB
SIMULATED_RULES = [
    {
        "id": "S3", 
        "name": "SSH Brute-Force Detection", 
        "description": "Détecte les tentatives répétées d'échecs d'authentification SSH.",
        "enabled": True, 
        "threshold": 3,
        "severity": "HIGH"
    },
    {
        "id": "S4", 
        "name": "UEBA - Behavioral Anomaly", 
        "description": "Détection d'anomalies comportementales (connexions hors-horaires, comptes inhabituels).",
        "enabled": True,
        "severity": "CRITICAL"
    },
    {
        "id": "S6", 
        "name": "Lateral Movement Detection", 
        "description": "Surveillance des rebonds suspects vers des infrastructures critiques (ex: DC Server).",
        "enabled": True,
        "severity": "CRITICAL"
    }
]

# --- 1. LISTER LES RÈGLES ---
@router.get("", status_code=status.HTTP_200_OK)
async def list_rules():
    """
    Récupère la liste de toutes les règles de corrélation logiques et comportementales actives dans le SIEM.
    """
    try:
        return {
            "total_rules": len(SIMULATED_RULES), 
            "rules": SIMULATED_RULES
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des règles : {str(e)}")


# --- 2. CRÉER UNE RÈGLE ---
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_rule(rule_data: dict):
    """
    Permet au Responsable Sécurité (SecOps) de créer une nouvelle règle de corrélation personnalisée.
    """
    try:
        # On simule l'attribution d'un ID
        new_rule = {
            "id": f"S{len(SIMULATED_RULES) + 1}",
            **rule_data
        }
        return {
            "status": "success", 
            "message": f"Nouvelle règle de sécurité {new_rule['id']} enregistrée avec succès.", 
            "rule": new_rule
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Échec de la création de la règle : {str(e)}")


# --- 3. MODIFIER UNE RÈGLE ---
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_rule(id: str, rule_data: dict):
    """
    Modifie à la volée les critères ou les seuils d'une règle existante (ex: changer le seuil d'échecs SSH).
    """
    try:
        # Recherche fictive de la règle pour validation
        rule_exists = any(r["id"] == id.upper() for r in SIMULATED_RULES)
        if not rule_exists:
            raise HTTPException(status_code=404, detail=f"La règle {id} n'existe pas.")
            
        return {
            "status": "success", 
            "message": f"Règle {id.upper()} mise à jour et rechargée dans le moteur de corrélation.",
            "updated_fields": rule_data
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- 4. SUPPRIMER/DÉSACTIVER UNE RÈGLE ---
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_rule(id: str):
    """
    Désactive ou supprime définitivement une règle du moteur de détection active du SIEM.
    """
    try:
        rule_exists = any(r["id"] == id.upper() for r in SIMULATED_RULES)
        if not rule_exists:
            raise HTTPException(status_code=404, detail=f"La règle {id} n'existe pas.")
            
        return {
            "status": "success", 
            "message": f"Règle {id.upper()} désactivée et retirée du cluster de corrélation avec succès."
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))