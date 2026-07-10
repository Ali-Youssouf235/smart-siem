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
SEUIL_LOGS_PAR_MINUTE = 20  # Maximum de logs autorisés par minute pour une machine standard
SEUIL_SCORE_CRITIQUE = 70   # Score de risque (0-100) au-delà duquel on lève une alerte CRITICAL

# 🟢 Catégorisation claire des alertes comportementales UEBA (même logique que
# CATALOGUE_REGLES dans app/core/engine.py, pour rester cohérent et simple).
CATALOGUE_UEBA = {
    "UEBA-HORS-HORAIRE": {
        "categorie": "Anomalie Comportementale - Connexion hors horaires",
        "tactique_mitre": "TA0001 - Initial Access",
        "technique_mitre": "T1078 - Valid Accounts",
    },
    "UEBA-SPIKE-VOLUME": {
        "categorie": "Anomalie Comportementale - Pic de volumétrie",
        "tactique_mitre": "TA0010 - Exfiltration",
        "technique_mitre": "T1030 - Data Transfer Size Limits",
    },
    "UEBA-SCORE-RISQUE-CRITIQUE": {
        "categorie": "Menace Interne - Score de risque critique",
        "tactique_mitre": "TA0010 - Exfiltration",
        "technique_mitre": "T1030 - Data Transfer Size Limits",
    },
}

# 🟢 SCORING DE RISQUE DYNAMIQUE (0-100) PAR ENTITÉ (host/utilisateur)
# Implémentation volontairement simple (dict en mémoire, pas de persistance)
# mais SUFFISANTE pour démontrer le scénario S7 (Nina Myers) en présentation :
# chaque anomalie fait monter le score, un score élevé déclenche une alerte
# CRITICAL même si aucune règle seule n'aurait suffi.
RISK_SCORES: Dict[str, int] = {}

POINTS_PAR_ANOMALIE = {
    "UEBA-HORS-HORAIRE": 35,
    "UEBA-SPIKE-VOLUME": 40,
}


def _augmenter_score_risque(entite: str, points: int) -> int:
    """Augmente le score de risque d'une entité (host/utilisateur), plafonné à 100."""
    nouveau_score = min(100, RISK_SCORES.get(entite, 0) + points)
    RISK_SCORES[entite] = nouveau_score
    return nouveau_score


def get_risk_score(entite: str) -> int:
    """Consultation du score de risque actuel d'une entité (pour le dashboard/API)."""
    return RISK_SCORES.get(entite, 0)


def detect_behavioral_anomalies(new_log: Dict) -> Optional[AlertBaseSchema]:
    """
    Analyse le comportement d'une entité (Hôte ou IP) pour détecter
    des déviations par rapport à la baseline (Règle S4 - UEBA), et met à jour
    son score de risque dynamique. Retourne l'alerte la plus critique déclenchée.
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
    alerte_a_retourner: Optional[AlertBaseSchema] = None

    # ─── 1. ANOMALIE HORAIRE (Heures suspectes / Travail de nuit) ───
    is_weekend = log_time.weekday() >= 5  # 5 = Samedi, 6 = Dimanche
    is_night = log_time.hour < HEURES_BUREAU_DEBUT or log_time.hour > HEURES_BUREAU_FIN

    if (is_night or is_weekend) and new_log.get("log_type") == "auth" and "Success" in new_log.get("raw_message", ""):
        logger.warning(f"⚠️ [UEBA] Connexion suspecte hors horaire sur {host} à {log_time.strftime('%H:%M:%S')}")
        score = _augmenter_score_risque(host, POINTS_PAR_ANOMALIE["UEBA-HORS-HORAIRE"])
        alerte_a_retourner = create_ueba_alert(
            regle_id="UEBA-HORS-HORAIRE",
            description=f"Activité d'authentification suspecte en dehors des heures de bureau sur l'hôte {host}. Score de risque : {score}/100.",
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
            score = _augmenter_score_risque(host, POINTS_PAR_ANOMALIE["UEBA-SPIKE-VOLUME"])
            alerte_a_retourner = create_ueba_alert(
                regle_id="UEBA-SPIKE-VOLUME",
                description=f"Pic d'activité anormal (DDoS ou Brute-force sauvage) : {recent_log_count} événements générés en 1 minute sur {host}. Score de risque : {score}/100.",
                host=host
            )
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la baseline volumétrique : {str(e)}")

    # ─── 3. ESCALADE : SCORE DE RISQUE CRITIQUE (comportement cumulé, scénario S7) ───
    # Même si aucune anomalie unitaire ci-dessus n'a suffi seule, l'accumulation de
    # plusieurs signaux faibles sur la même entité doit produire une alerte CRITICAL
    # dédiée — c'est ce qui distingue l'UEBA d'un simple empilement de règles.
    if get_risk_score(host) >= SEUIL_SCORE_CRITIQUE:
        alerte_a_retourner = create_ueba_alert(
            regle_id="UEBA-SCORE-RISQUE-CRITIQUE",
            description=f"Score de risque comportemental critique pour {host} : {get_risk_score(host)}/100. Plusieurs signaux faibles corrélés (horaires + volumétrie).",
            host=host
        )

    return alerte_a_retourner


def create_ueba_alert(regle_id: str, description: str, host: str) -> AlertBaseSchema:
    """Helper pour générer et enregistrer l'alerte comportementale, correctement catégorisée."""
    meta = CATALOGUE_UEBA.get(regle_id, {})
    nouvelle_alerte = AlertBaseSchema(
        id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.utcnow(),
        niveau_criticite="CRITICAL" if regle_id == "UEBA-SCORE-RISQUE-CRITIQUE" else "HIGH",
        statut="ouvert",
        regle_id=regle_id,
        utilisateur_id=None,
        categorie=meta.get("categorie", "Anomalie Comportementale"),
        tactique_mitre=meta.get("tactique_mitre"),
        technique_mitre=meta.get("technique_mitre"),
        description=description,
        sources_correlees=["comportemental"],
    )

    # Stockage direct de l'alerte comportementale dans Elasticsearch pour alimenter ton Dashboard !
    if es_client:
        alerte_dict = nouvelle_alerte.model_dump()
        alerte_dict["timestamp"] = alerte_dict["timestamp"].isoformat()
        alerte_dict["cible_host"] = host
        alerte_dict["score_risque"] = get_risk_score(host)
        es_client.index(index="smart-siem-logs", id=nouvelle_alerte.id, document=alerte_dict)

    return nouvelle_alerte