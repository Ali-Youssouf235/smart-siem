from datetime import datetime
from typing import Optional, Dict
import logging
from app.schemas.alert_schema import AlertBaseSchema
from app.core.database import es_client
import uuid

logger = logging.getLogger("smart-siem")

# Configuration des seuils comportementaux du SIEM
HEURES_BUREAU_DEBUT = 7   # 07:00
HEURES_BUREAU_FIN = 19    # 19:00
SEUIL_LOGS_PAR_MINUTE = 20 # Maximum de logs autorisés par minute pour une machine standard

def detect_behavioral_anomalies(new_log: Dict) -> Optional[AlertBaseSchema]:
    """
    Analyse le comportement d'une entité (Hôte ou IP) pour détecter 
    des déviations par rapport à la baseline (Règle S4 - UEBA).
    """
    global es_client
    if not es_client:
        return None

    # Extraction des données de temps
    try:
        if isinstance(new_log["timestamp"], str):
            log_time = datetime.fromisoformat(new_log["timestamp"].replace("Z", "+00:00"))
        else:
            log_time = new_log["timestamp"]
    except Exception:
        log_time = datetime.utcnow()

    host = new_log.get("host", "unknown-host")
    
    # ─── 1. ANOMALIE HORAIRE (Heures suspectes / Travail de nuit) ───
    is_weekend = log_time.weekday() >= 5 # 5 = Samedi, 6 = Dimanche
    is_night = log_time.hour < HEURES_BUREAU_DEBUT or log_time.hour > HEURES_BUREAU_FIN
    
    # Si c'est un log d'authentification ou d'accès réussi en pleine nuit/weekend
    if (is_night or is_weekend) and new_log.get("log_type") == "auth" and "Success" in new_log.get("raw_message", ""):
        logger.warning(f"⚠️ [UEBA] Connexion suspecte hors horaire sur {host} à {log_time.strftime('%H:%M:%S')}")
        
        return create_ueba_alert(
            regle_id="UEBA-HORS-HORAIRE",
            description=f"Activité d'authentification suspecte en dehors des heures de bureau sur l'hôte {host}.",
            host=host
        )

    # ─── 2. ANOMALIE DE VOLUME (Pic d'activité anormal) ───
    # On demande à Elasticsearch combien de logs cet hôte a généré durant la dernière minute
    try:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"host.keyword": host}},
                        {"range": {"timestamp": {"gte": "now-1m"}}}
                    ]
                }
            }
        }
        response = es_client.count(index="smart-siem-logs", body=query)
        recent_log_count = response["count"]

        if recent_log_count > SEUIL_LOGS_PAR_MINUTE:
            logger.error(f"🚨 [UEBA] Volumétrie critique détectée sur {host} : {recent_log_count} logs/min (Seuil: {SEUIL_LOGS_PAR_MINUTE})")
            
            return create_ueba_alert(
                regle_id="UEBA-SPIKE-VOLUME",
                description=f"Pic d'activité anormal (DDoS ou Brute-force sauvage) : {recent_log_count} événements générés en 1 minute.",
                host=host
            )
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la baseline volumétrique : {str(e)}")

    return None

def create_ueba_alert(regle_id: str, description: str, host: str) -> AlertBaseSchema:
    """Helper pour générer et enregistrer l'alerte comportementale"""
    nouvelle_alerte = AlertBaseSchema(
        id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.utcnow(),
        niveau_criticite="HIGH",
        statut="ouvert",
        regle_id=regle_id,
        utilisateur_id=None
    )
    
    # Stockage direct de l'alerte comportementale dans Elasticsearch pour alimenter ton Dashboard !
    if es_client:
        alerte_dict = nouvelle_alerte.model_dump()
        alerte_dict["timestamp"] = alerte_dict["timestamp"].isoformat()
        alerte_dict["description"] = description
        alerte_dict["cible_host"] = host
        es_client.index(index="smart-siem-logs", id=nouvelle_alerte.id, document=alerte_dict)
        
    return nouvelle_alerte