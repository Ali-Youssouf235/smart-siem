from datetime import datetime, timedelta
from typing import List, Optional
from app.schemas.log_schema import LogBaseSchema
from app.schemas.alert_schema import AlertBaseSchema
from app.core.database import save_log_to_elasticsearch, es_client # On récupère le client Elastic
import uuid

LOG_BUFFER: List[LogBaseSchema] = []
ALERTE_STORAGE_GLOBAL: List[AlertBaseSchema] = []

# 🟢 NOUVEAUTÉ SOAR : Fonction de remédiation automatique (Table LOGS_ACTIONS_INCIDENTS)
def trigger_soar_playbook(alerte_id: str, action_type: str, cible_ip: str):
    """Simule une action corrective automatique et l'enregistre dans Elasticsearch."""
    action_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
    timestamp_act = datetime.utcnow().isoformat()
    
    # Message de description dynamique conforme à ton dictionnaire de données
    description = f"Playbook SOAR déclenché automatiquement. Commande exécutée : [iptables -A INPUT -s {cible_ip} -j DROP]. Statut : Succès."
    
    action_document = {
        "id": action_id,
        "action_type": action_type,         # ex: "blocage d'IP"
        "timestamp": timestamp_act,
        "description": description,
        "alerte_id": alerte_id              # Lien direct avec l'alerte générée
    }
    
    # On pousse l'action corrective dans l'index dédié d'Elasticsearch
    try:
        if es_client:
            es_client.index(index="smart-siem-actions", id=action_id, document=action_document)
            print(f"⚡ [SOAR PLAYBOOK] Action {action_id} enregistrée avec succès dans Elastic : IP {cible_ip} bloquée.")
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement de l'action SOAR : {e}")


def check_brute_force_ssh(new_log: LogBaseSchema) -> Optional[AlertBaseSchema]:
    """Scénario S3 : Détecte 5 échecs de connexion SSH en moins de 60 secondes."""
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
        
        # 🟢 LES DEUX LIGNES COMPLÉMENTAIRES POUR LES STATS :
        if es_client:
            alerte_dict = nouvelle_alerte.model_dump()
            alerte_dict["timestamp"] = alerte_dict["timestamp"].isoformat()
            # On stocke l'alerte dans 'smart-siem-logs' pour que notre route GET/stats la trouve !
            es_client.index(index="smart-siem-logs", id=nouvelle_alerte.id, document=alerte_dict)
        
        # APPEL DU SOAR : L'alerte est levée, on bloque instantanément l'adresse IP source !
        trigger_soar_playbook(
            alerte_id=nouvelle_alerte.id, 
            action_type="blocage d'IP", 
            cible_ip=new_log.source_ip
        )
        
        return nouvelle_alerte
    
    return None

def check_lateral_movement(new_log: LogBaseSchema) -> Optional[AlertBaseSchema]:
    """Scénario S6 : Détecte une même IP se connectant à plus de 3 hôtes différents en 5 min."""
    global LOG_BUFFER, ALERTE_STORAGE_GLOBAL
    
    if new_log not in LOG_BUFFER:
        LOG_BUFFER.append(new_log)
    
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
        
        # 🟢 APPEL DU SOAR : On applique aussi un playbook pour le mouvement latéral
        trigger_soar_playbook(
            alerte_id=nouvelle_alerte.id, 
            action_type="isolation de machine", 
            cible_ip=new_log.source_ip
        )
        
        return nouvelle_alerte
        
    return None