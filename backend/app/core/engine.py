from datetime import datetime, timedelta
from typing import List, Optional
from app.schemas.log_schema import LogBaseSchema
from app.schemas.alert_schema import AlertBaseSchema
import uuid

# Mémoire tampon partagée pour stocker tous les logs récents
LOG_BUFFER: List[LogBaseSchema] = []
ALERTE_STORAGE_GLOBAL: List[AlertBaseSchema] = []

def check_brute_force_ssh(new_log: LogBaseSchema) -> Optional[AlertBaseSchema]:
    """Scénario S3 : Détecte 5 échecs de connexion SSH en moins de 60 secondes."""
    global LOG_BUFFER, ALERTE_STORAGE_GLOBAL
    
    # NOTE: L'ajout au LOG_BUFFER est maintenant géré de manière centrale ou par la première règle
    if new_log not in LOG_BUFFER:
        LOG_BUFFER.append(new_log)
        
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
    
    # CORRECTION : On s'assure que le log actuel est bien dans le tampon pour l'analyse !
    if new_log not in LOG_BUFFER:
        LOG_BUFFER.append(new_log)
    
    if new_log.log_type not in ["auth", "réseau"] or "Failed" in new_log.raw_message:
        return None
        
    temps_limite = new_log.timestamp - timedelta(seconds=300)
    
    # On cherche toutes les connexions réussies de cette IP depuis 5 min
    connexions_recentes = [
        log for log in LOG_BUFFER
        if log.source_ip == new_log.source_ip
        and log.timestamp >= temps_limite
        and log.log_type in ["auth", "réseau"]
        and "Failed" not in log.raw_message
    ]
    
    hotes_visites = set(log.host for log in connexions_recentes)
    
    # Si l'IP a visité 3 hôtes ou plus, on déclenche !
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