from datetime import datetime, timedelta
from typing import List, Dict
from app.schemas.log_schema import LogBaseSchema
from app.schemas.alert_schema import AlertBaseSchema
import uuid

# Mémoire tampon temporaire pour stocker les logs récents le temps de l'analyse
LOG_BUFFER: List[LogBaseSchema] = []

def check_brute_force_ssh(new_log: LogBaseSchema) -> Optional[AlertBaseSchema]:
    """
    Scénario S3 : Détecte si un hôte subit 5 échecs de connexion en moins de 60 secondes.
    """
    global LOG_BUFFER
    
    # 1. On ajoute le nouveau log au tampon
    LOG_BUFFER.append(new_log)
    
    # 2. On définit la fenêtre de temps (60 secondes en arrière par rapport au log actuel)
    temps_limite = new_log.timestamp - timedelta(seconds=60)
    
    # 3. On nettoie le tampon pour ne garder que les logs des 60 dernières secondes
    LOG_BUFFER = [log for log in LOG_BUFFER if log.timestamp >= temps_limite]
    
    # 4. Si le log actuel n'est pas un échec d'authentification SSH, pas besoin d'aller plus loin
    if new_log.log_type != "auth" or "Failed password" not in new_log.raw_message:
        return None
        
    # 5. On compte combien d'échecs ont eu lieu sur le MÊME hôte cible dans cette fenêtre de 60s
    echecs_sur_hote = [
        log for log in LOG_BUFFER 
        if log.host == new_log.host 
        and log.log_type == "auth" 
        and "Failed password" in log.raw_message
    ]
    
    # 6. REGLE DE CORRELATION : Si le nombre d'échecs >= 5, on déclenche une alerte !
    if len(echecs_sur_hote) >= 5:
        # On crée l'objet Alerte basé sur notre alert_schema
        nouvelle_alerte = AlertBaseSchema(
            id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.utcnow(),
            niveau_criticite="CRITICAL",
            statut="ouvert",
            regle_id="MITRE-T1110-BRUTEFORCE",
            utilisateur_id=None
        )
        return nouvelle_alerte
        
    return None