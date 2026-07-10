"""
Catégorisation des événements du Smart SIEM.

Objectif : que CHAQUE log ingéré et CHAQUE alerte générée porte une
catégorie claire et lisible par un humain (ex: "Authentification",
"Mouvement Latéral", "Intrusion / Malware") — et non un champ vide ou un
identifiant de règle brut type "MITRE-T1110-BRUTEFORCE".

Volontairement simple, comme demandé : un dictionnaire de correspondances
et quelques mots-clés. Pas de machine learning, pas de scoring complexe.
"""

# ─────────────────────────────────────────────────────────────────────────
# 1. CATÉGORIES DES LOGS BRUTS (à l'ingestion)
# ─────────────────────────────────────────────────────────────────────────
# Point de départ : le log_type déjà détecté par le parser (format source).
LOG_TYPE_TO_CATEGORY = {
    "auth": "Authentification",
    "syslog": "Authentification",
    "firewall": "Accès Réseau / Pare-feu",
    "réseau": "Accès Réseau / Pare-feu",
    "network": "Accès Réseau / Pare-feu",
    "vpn": "Accès Réseau / Pare-feu",
    "ids/ips": "Intrusion / Malware",
    "wazuh": "Intrusion / Malware",
    "fail2ban": "Intrusion / Malware",
    "web": "Application Web",
    "database": "Base de Données",
    "dns": "Infrastructure Réseau",
    "dhcp": "Infrastructure Réseau",
    "windows": "Système / Poste de Travail",
    "container": "Système / Conteneurs",
    "kubernetes": "Système / Conteneurs",
    "json": "Application",
    "inconnu": "Non Catégorisé",
}

# Mots-clés qui priment sur le type source par défaut : un log "firewall"
# qui contient "exploit" doit rester classé comme intrusion, pas comme
# simple trafic réseau. Vérifiés dans l'ordre ci-dessous.
KEYWORD_OVERRIDES = [
    ("Intrusion / Malware", ["malware", "virus", "exploit", "intrusion", "shellcode", "ransomware", "injection", "sql injection"]),
    ("Authentification (Anomalie)", ["failed password", "authentication failed", "login failed", "account locked", "brute"]),
    ("Accès Réseau / Pare-feu", ["drop", "deny", " block ", "port scan"]),
]


def categorize_log(log_type: str, raw_message: str, severity: str = "") -> str:
    """Retourne une catégorie claire pour un log brut."""
    message_lower = f" {(raw_message or '').lower()} "

    for category, keywords in KEYWORD_OVERRIDES:
        if any(kw in message_lower for kw in keywords):
            return category

    return LOG_TYPE_TO_CATEGORY.get((log_type or "").lower(), "Activité Système Générale")


# ─────────────────────────────────────────────────────────────────────────
# 2. CATÉGORIES DES ALERTES (moteur de corrélation + UEBA)
# ─────────────────────────────────────────────────────────────────────────
# Indexé par regle_id : plus fiable qu'un parsing de texte, puisque c'est
# le moteur de corrélation lui-même qui fixe ce code.
RULE_ID_TO_CATEGORY = {
    "MITRE-T1110-BRUTEFORCE": "Authentification (Force Brute)",
    "MITRE-T1081-LATERAL-MOVEMENT": "Mouvement Latéral",
    "UEBA-HORS-HORAIRE": "Comportement Utilisateur (UEBA)",
    "UEBA-SPIKE-VOLUME": "Déni de Service / Volumétrie",
}


def categorize_alert(regle_id: str) -> str:
    """Retourne une catégorie claire pour une alerte, à partir de sa règle déclencheuse."""
    return RULE_ID_TO_CATEGORY.get(regle_id, "Non Catégorisé")
