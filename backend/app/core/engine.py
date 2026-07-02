from datetime import datetime, timedelta
from typing import List, Optional
from app.schemas.log_schema import LogBaseSchema
from app.schemas.alert_schema import AlertBaseSchema
from app.core.database import save_log_to_elasticsearch, es_client
import uuid

LOG_BUFFER: List[LogBaseSchema] = []
ALERTE_STORAGE_GLOBAL: List[AlertBaseSchema] = []


def trigger_soar_playbook(alerte_id: str, action_type: str, cible_ip: str):
    """Simule une action corrective automatique et l'enregistre dans Elasticsearch."""
    action_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
    timestamp_act = datetime.utcnow().isoformat()

    description = (
        f"Playbook SOAR declenche automatiquement. "
        f"Commande executee : [iptables -A INPUT -s {cible_ip} -j DROP]. "
        f"Statut : Succes."
    )

    action_document = {
        "id": action_id,
        "action_type": action_type,
        "timestamp": timestamp_act,
        "description": description,
        "alerte_id": alerte_id
    }

    try:
        if es_client:
            es_client.index(
                index="smart-siem-actions",
                id=action_id,
                document=action_document
            )
            print(f"[SOAR] Action {action_id} enregistree : IP {cible_ip} bloquee.")
    except Exception as e:
        print(f"Erreur enregistrement action SOAR : {e}")


def check_brute_force_ssh(new_log: LogBaseSchema) -> Optional[AlertBaseSchema]:
    """Scenario S3 : Detecte 5 echecs de connexion SSH en moins de 60 secondes."""
    global LOG_BUFFER, ALERTE_STORAGE_GLOBAL

    if new_log not in LOG_BUFFER:
        LOG_BUFFER.append(new_log)
        log_dict = new_log.model_dump()
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

        if es_client:
            alerte_dict = nouvelle_alerte.model_dump()
            alerte_dict["timestamp"] = alerte_dict["timestamp"].isoformat()
            es_client.index(
                index="smart-siem-logs",
                id=nouvelle_alerte.id,
                document=alerte_dict
            )

        trigger_soar_playbook(
            alerte_id=nouvelle_alerte.id,
            action_type="blocage d'IP",
            cible_ip=new_log.source_ip
        )

        return nouvelle_alerte

    return None


def check_lateral_movement(new_log: LogBaseSchema) -> Optional[AlertBaseSchema]:
    """Scenario S6 : Detecte une meme IP se connectant a plus de 3 hotes en 5 min."""
    global LOG_BUFFER, ALERTE_STORAGE_GLOBAL

    if new_log not in LOG_BUFFER:
        LOG_BUFFER.append(new_log)

    if new_log.log_type not in ["auth", "reseau"] or "Failed" in new_log.raw_message:
        return None

    temps_limite = new_log.timestamp - timedelta(seconds=300)

    connexions_recentes = [
        log for log in LOG_BUFFER
        if log.source_ip == new_log.source_ip
           and log.timestamp >= temps_limite
           and log.log_type in ["auth", "reseau"]
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

        trigger_soar_playbook(
            alerte_id=nouvelle_alerte.id,
            action_type="isolation de machine",
            cible_ip=new_log.source_ip
        )

        return nouvelle_alerte

    return None