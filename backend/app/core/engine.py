from datetime import datetime, timedelta
from typing import List, Optional
from app.schemas.log_schema import LogBaseSchema
from app.schemas.alert_schema import AlertBaseSchema
from app.core.database import save_log_to_elasticsearch, es_client # On récupère le client Elastic
import uuid

LOG_BUFFER: List[LogBaseSchema] = []
ALERTE_STORAGE_GLOBAL: List[AlertBaseSchema] = []

INDEX_RULES = "smart-siem-rules"

# 🟢 CATALOGUE DE CATÉGORISATION
# Table de correspondance unique regle_id -> catégorie lisible + tactique/technique
# MITRE ATT&CK. C'est ici, et ici seulement, que se définit "ce que veut dire"
# chaque règle : si on ajoute une règle demain, on ajoute une ligne ici et toutes
# les alertes qu'elle génère sont automatiquement catégorisées clairement.
CATALOGUE_REGLES = {
    "MITRE-T1110-BRUTEFORCE": {
        "categorie": "Brute Force SSH",
        "tactique_mitre": "TA0001 - Initial Access",
        "technique_mitre": "T1110 - Brute Force",
    },
    "MITRE-T1081-LATERAL-MOVEMENT": {
        "categorie": "Mouvement Latéral",
        "tactique_mitre": "TA0008 - Lateral Movement",
        "technique_mitre": "T1021 - Remote Services",
    },
}


def get_rule_config(rule_id: str, default_threshold: int, default_severity: str):
    """
    🟢 Lit la configuration réelle d'une règle (seuil, sévérité) depuis
    Elasticsearch (index smart-siem-rules), pour que le CRUD des règles
    (créer/modifier/supprimer depuis l'interface Règles) ait un effet concret
    et immédiat sur le moteur de corrélation — sans cette fonction, modifier
    une règle depuis le front ne changeait strictement rien à la détection.
    """
    if not es_client:
        return default_threshold, default_severity
    try:
        result = es_client.get(index=INDEX_RULES, id=rule_id, ignore=[404])
        if result and result.get("found"):
            src = result["_source"]
            if src.get("enabled") is False:
                return None, None  # règle désactivée : aucune détection
            return src.get("threshold", default_threshold), src.get("severity", default_severity)
    except Exception:
        pass
    return default_threshold, default_severity

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
    
    seuil, severite = get_rule_config("S3", default_threshold=5, default_severity="CRITICAL")
    if seuil is None:  # règle S3 désactivée depuis l'interface
        return None

    if len(echecs_sur_hote) >= seuil:
        meta = CATALOGUE_REGLES["MITRE-T1110-BRUTEFORCE"]
        nouvelle_alerte = AlertBaseSchema(
            id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.utcnow(),
            niveau_criticite=severite,
            statut="ouvert",
            regle_id="MITRE-T1110-BRUTEFORCE",
            utilisateur_id=None,
            categorie=meta["categorie"],
            tactique_mitre=meta["tactique_mitre"],
            technique_mitre=meta["technique_mitre"],
            description=(
                f"{len(echecs_sur_hote)} échecs d'authentification SSH détectés sur "
                f"l'hôte {new_log.host} en moins de 60 secondes, depuis l'IP {new_log.source_ip}."
            ),
            sources_correlees=["auth"],
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
    
    seuil, severite = get_rule_config("S6", default_threshold=3, default_severity="HIGH")
    if seuil is None:  # règle S6 désactivée depuis l'interface
        return None

    if len(hotes_visites) >= seuil:
        meta = CATALOGUE_REGLES["MITRE-T1081-LATERAL-MOVEMENT"]
        # Sources réellement combinées pour lever cette alerte (met en évidence
        # la corrélation inter-sources quand plusieurs types de logs sont impliqués)
        sources = sorted(set(log.log_type for log in connexions_recentes))
        nouvelle_alerte = AlertBaseSchema(
            id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.utcnow(),
            niveau_criticite=severite,
            statut="ouvert",
            regle_id="MITRE-T1081-LATERAL-MOVEMENT",
            utilisateur_id=None,
            categorie=meta["categorie"],
            tactique_mitre=meta["tactique_mitre"],
            technique_mitre=meta["technique_mitre"],
            description=(
                f"L'IP {new_log.source_ip} s'est connectée à {len(hotes_visites)} hôtes "
                f"différents ({', '.join(sorted(hotes_visites))}) en moins de 5 minutes."
            ),
            sources_correlees=sources,
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