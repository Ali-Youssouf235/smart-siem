from datetime import datetime, timedelta
from typing import List, Optional
from app.schemas.log_schema import LogBaseSchema
from app.schemas.alert_schema import AlertBaseSchema
import uuid

# Mémoire tampon temporaire pour stocker les logs récents
LOG_BUFFER: List[LogBaseSchema] = []

# LA CORRECTION EST ICI : C'est le moteur qui stocke la liste globale des alertes désormais
ALERTE_STORAGE_GLOBAL: List[AlertBaseSchema] = []

def check_brute_force_ssh(new_log: LogBaseSchema) -> Optional[AlertBaseSchema]:
    """
    Scénario S3 : Détecte si un hôte subit 5 échecs de connexion en moins de 60 secondes.
    """
    global LOG_BUFFER, ALERTE_STORAGE_GLOBAL
    
    LOG_BUFFER.append(new_log)
    temps_limite = new_log.timestamp - timedelta(seconds=60)
    LOG_BUFFER = [log for log in LOG_BUFFER if log.timestamp >= temps_limite]
    
    if new_log.log_type != "auth" or "Failed password" not in new_log.raw_message:
        return None
        
    echecs_sur_hote = [
        log for log in LOG_BUFFER 
        if log.host == new_log.host 
        and log.log_type == "auth" 
        and "Failed password" in log.raw_message
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
        # On l'enregistre directement ici
        ALERTE_STORAGE_GLOBAL.append(nouvelle_alerte)
        return nouvelle_alerte
        
    return None