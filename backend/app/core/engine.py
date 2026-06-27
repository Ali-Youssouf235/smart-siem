from datetime import datetime, timedelta
from typing import List, Optional
from app.schemas.log_schema import LogBaseSchema
from app.schemas.alert_schema import AlertBaseSchema
from app.core.database import save_log_to_elasticsearch # On importe notre nouvelle fonction !
import uuid

# Le LOG_BUFFER reste utile temporairement pour la corrélation en temps réel (fenêtre de 5min)
LOG_BUFFER: List[LogBaseSchema] = []
ALERTE_STORAGE_GLOBAL: List[AlertBaseSchema] = []

def check_brute_force_ssh(new_log: LogBaseSchema) -> Optional[AlertBaseSchema]:
    """Scénario S3 : Détecte 5 échecs de connexion SSH en moins de 60 secondes."""
    global LOG_BUFFER, ALERTE_STORAGE_GLOBAL
    
    if new_log not in LOG_BUFFER:
        LOG_BUFFER.append(new_log)
        
        # SAUVEGARDE PROFESSIONNELLE : On convertit le schéma en dictionnaire JSON et on l'envoie à Elastic
        log_dict = new_log.model_dump()
        # On s'assure que la date est au format texte ISO pour Elasticsearch
        log_dict["timestamp"] = log_dict["timestamp"].isoformat()
        save_log_to_elasticsearch(log_dict)

    temps_limite = new_log.timestamp - timedelta(seconds=60)
    
    if new_log.log_type != "auth" or "Failed password" not in new_log.raw_message:
        return None
        
    echecs_sur_hote = [
        log for log in LOG_BUFFER 
        if log.host == new_log.host 
        and log.log_type == "auth" 
        and "Failed password" in log.raw_message
        and log.timestamp >= temps_limite
    ]
    
    if len(echecs_sur_hote) >= 5:
        nouvelle_alerte = AlertBaseSchema(
            id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.utcnow(),
            niveau_criticite="CRITICAL",
            statut="ouvert",
            regle_id="MITRE-T1110-BRUTEFORCE",
            utilisateur_id=None
        )
        ALERTE_STORAGE_GLOBAL.append(nouvelle_alerte)
        return nouvelle_alerte
        
    return None

def check_lateral_movement(new_log: LogBaseSchema) -> Optional[AlertBaseSchema]:
    """Scénario S6 : Détecte une même IP se connectant à plus de 3 hôtes différents en 5 min."""
    global LOG_BUFFER, ALERTE_STORAGE_GLOBAL
    
    if new_log not in LOG_BUFFER:
        LOG_BUFFER.append(new_log)
        # Pas besoin de save_log_to_elasticsearch ici, car le log est déjà sauvegardé par la règle du haut 
        # s'il n'était pas dans le buffer.
    
    if new_log.log_type not in ["auth", "réseau"] or "Failed" in new_log.raw_message:
        return None
        
    temps_limite = new_log.timestamp - timedelta(seconds=300)
    
    connexions_recentes = [
        log for log in LOG_BUFFER
        if log.source_ip == new_log.source_ip
        and log.timestamp >= temps_limite
        and log.log_type in ["auth", "réseau"]
        and "Failed" not in log.raw_message
    ]
    
    hotes_visites = set(log.host for log in connexions_recentes)
    
    if len(hotes_visites) >= 3:
        nouvelle_alerte = AlertBaseSchema(
            id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.utcnow(),
            niveau_criticite="HIGH",
            statut="ouvert",
            regle_id="MITRE-T1081-LATERAL-MOVEMENT",
            utilisateur_id=None
        )
        ALERTE_STORAGE_GLOBAL.append(nouvelle_alerte)
        return nouvelle_alerte
        
    return None