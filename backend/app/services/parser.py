import re
import uuid
from datetime import datetime
from typing import Optional, Dict, List

# ══════════════════════════════════════════════════════════════════════════════
#  SMART SIEM — UNIVERSAL LOG PARSER
#  Couvre : Linux Syslog, SSH, Wireshark/Tcpdump, Apache/Nginx, Windows Event,
#           Firewall (iptables/Cisco/Palo Alto), CEF, JSON, Suricata/Snort IDS,
#           Wazuh, Fail2Ban, PostgreSQL/MySQL, VPN (OpenVPN/WireGuard),
#           DHCP, DNS Bind9, Docker/Kubernetes
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# 1. DICTIONNAIRE DES REGEX PAR FORMAT
# ─────────────────────────────────────────────────────────────────────────────

REGEX_PATTERNS = {

    # ── LINUX / UNIX SYSLOG (RFC 3164) ──────────────────────────────────────
    # Ex: Jan  5 06:25:14 server01 sshd[12345]: Failed password for root from 192.168.1.10
    "linux_syslog": re.compile(
        r"^(?P<timestamp>\w{3}\s{1,2}\d{1,2}\s+\d{2}:\d{2}:\d{2})"
        r"\s+(?P<host>[\w.\-]+)"
        r"\s+(?P<process>[\w.\-\/%]+)(?:\[(?P<pid>\d+)\])?:\s+"
        r"(?P<message>.+)$"
    ),

    # ── SYSLOG RFC 5424 (format structuré moderne) ───────────────────────────
    # Ex: <34>1 2026-01-05T06:25:14Z server01 sshd 12345 ID47 - BOM message
    "syslog_rfc5424": re.compile(
        r"^<(?P<priority>\d+)>(?P<version>\d)\s+"
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\w:.+-]*)\s+"
        r"(?P<host>[\w.\-]+)\s+(?P<app>[\w.\-]+)\s+(?P<pid>[\d-]+)\s+"
        r"(?P<msgid>[\w-]+)\s+(?P<structured_data>-|\[.*?\])\s+"
        r"(?P<message>.+)$"
    ),

    # ── CISCO IOS / NX-OS (Syslog) ───────────────────────────────────────────

    "cisco_ios": re.compile(
    r"^(?P<timestamp>\w{3}\s{1,2}\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>[\w.\-]+)\s+"
    r"%(?P<facility>[\w_]+)-(?P<level>\d)-(?P<mnemonic>[\w_]+):\s+"
    r"(?P<message>.+)$"
    ),

    # ── APACHE ACCESS LOG (Combined Log Format) ──────────────────────────────
    # Ex: 192.168.1.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 2326
    "apache_access": re.compile(
        r'^(?P<src_ip>[\d.]+)\s+\S+\s+(?P<user>\S+)\s+'
        r'\[(?P<timestamp>[^\]]+)\]\s+'
        r'"(?P<method>\w+)\s+(?P<path>\S+)\s+(?P<protocol>[^"]+)"\s+'
        r'(?P<status>\d{3})\s+(?P<size>\d+|-)'
        r'(?:\s+"(?P<referer>[^"]*)"\s+"(?P<user_agent>[^"]*)")?$'
    ),

    # ── NGINX ACCESS LOG ─────────────────────────────────────────────────────
    # Ex: 127.0.0.1 - - [04/Nov/2021:14:09:01 +0000] "GET / HTTP/1.1" 200 396 "-" "curl/7.68.0"
    "nginx_access": re.compile(
        r'^(?P<src_ip>[\d.]+)\s+-\s+(?P<user>\S+)\s+'
        r'\[(?P<timestamp>[^\]]+)\]\s+'
        r'"(?P<method>\w+)\s+(?P<path>\S+)\s+(?P<protocol>[^"]+)"\s+'
        r'(?P<status>\d{3})\s+(?P<size>\d+)\s+'
        r'"(?P<referer>[^"]*)"\s+"(?P<user_agent>[^"]*)"$'
    ),

    # ── NGINX ERROR LOG ──────────────────────────────────────────────────────
    # Ex: 2021/11/04 14:09:01 [error] 1234#1234: *1 connect() failed (111)
    "nginx_error": re.compile(
        r'^(?P<timestamp>\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'\[(?P<level>\w+)\]\s+(?P<pid>\d+)#(?P<tid>\d+):\s+'
        r'(?P<message>.+)$'
    ),

    # ── WIRESHARK / TCPDUMP ──────────────────────────────────────────────────
    # Ex: 1  0.000000  192.168.1.1  8.8.8.8  DNS  72  Standard query
    "wireshark": re.compile(
        r'^\d+\s+[\d.]+\s+'
        r'(?P<src_ip>[\d.a-fA-F:]+)\s+'
        r'(?P<dst_ip>[\d.a-fA-F:]+)\s+'
        r'(?P<proto>\w+)\s+(?P<len>\d+)\s+'
        r'(?P<msg>.+)$'
    ),

    # ── WINDOWS EVENT LOG (format texte exporté) ─────────────────────────────
    # Ex: 2026-01-05 06:25:14 EventID=4625 Level=Error Source=Security
    "windows_event": re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'EventID=(?P<event_id>\d+)\s+'
        r'Level=(?P<level>\w+)\s+'
        r'Source=(?P<source>[\w\s]+?)\s+'
        r'(?:Computer=(?P<computer>[\w.\-]+)\s+)?'
        r'(?:User=(?P<user>[\w\\.\-]+)\s+)?'
        r'(?P<message>.*)$'
    ),

    # ── WINDOWS EVENT XML simplifié ──────────────────────────────────────────
    # Ex: <EventID>4625</EventID> dans un flux
    "windows_event_xml": re.compile(
        r'<EventID>(?P<event_id>\d+)</EventID>.*?'
        r'<TimeCreated\s+SystemTime=[\'"](?P<timestamp>[^\'"]+)[\'"]',
        re.DOTALL
    ),

    # ── IPTABLES / NETFILTER ─────────────────────────────────────────────────
    # Ex: Jan  5 06:25:14 fw01 kernel: [UFW BLOCK] IN=eth0 SRC=10.0.0.1 DST=10.0.0.2 PROTO=TCP SPT=443 DPT=80
    "iptables": re.compile(
        r'^(?P<timestamp>\w{3}\s{1,2}\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<host>[\w.\-]+)\s+\w+:\s+'
        r'(?:\[[\d. ]+\])?\s*\[?(?P<action>[\w\s]+)\]?'
        r'(?:\s+IN=(?P<in_iface>\w*))?'
        r'(?:\s+OUT=(?P<out_iface>\w*))?'
        r'(?:.*\sSRC=(?P<src_ip>[\d.]+))?'
        r'(?:.*\sDST=(?P<dst_ip>[\d.]+))?'
        r'(?:.*\sPROTO=(?P<proto>\w+))?'
        r'(?:.*\sSPT=(?P<src_port>\d+))?'
        r'(?:.*\sDPT=(?P<dst_port>\d+))?'
        r'(?P<rest>.*)$'
    ),

    # ── CISCO ASA FIREWALL ───────────────────────────────────────────────────
    # Ex: %ASA-6-302013: Built inbound TCP connection 123 for inside:10.0.0.1/1234 to outside:8.8.8.8/443
    "cisco_asa": re.compile(
        r'%ASA-(?P<level>\d)-(?P<msg_id>\d+):\s+(?P<action>[\w\s]+)'
        r'.*?(?P<proto>TCP|UDP|ICMP)?\s+'
        r'(?:connection\s+\S+\s+)?'
        r'(?:for\s+\S+:(?P<src_ip>[\d.]+)/(?P<src_port>\d+)\s+to\s+\S+:(?P<dst_ip>[\d.]+)/(?P<dst_port>\d+))?'
        r'(?P<message>.*)$'
    ),

    # ── PALO ALTO FIREWALL (CSV) ─────────────────────────────────────────────
    # Ex: TRAFFIC,start,2026/01/05,10:00:00,vsys1,untrust,trust,...,1.2.3.4,5.6.7.8,TCP,...
    "palo_alto": re.compile(
        r'^(?P<type>TRAFFIC|THREAT|SYSTEM),(?P<subtype>\w+),'
        r'(?P<timestamp>\d{4}/\d{2}/\d{2},\d{2}:\d{2}:\d{2}),'
        r'(?P<vsys>[\w]+),'
        r'(?P<src_zone>[\w\-]+),(?P<dst_zone>[\w\-]+),'
        r'(?:.*?,){4}'
        r'(?P<src_ip>[\d.]+),(?P<dst_ip>[\d.]+),'
        r'(?P<proto>TCP|UDP|ICMP|[\w]+),'
    ),

    # ── CEF — Common Event Format (ArcSight, SIEM standard) ─────────────────
    # Ex: CEF:0|Security|Intrusion|1.0|100|Detected|7|src=192.168.1.1 dst=10.0.0.1
    "cef": re.compile(
        r'^CEF:(?P<version>\d+)\|'
        r'(?P<device_vendor>[^|]*)\|'
        r'(?P<device_product>[^|]*)\|'
        r'(?P<device_version>[^|]*)\|'
        r'(?P<signature_id>[^|]*)\|'
        r'(?P<name>[^|]*)\|'
        r'(?P<severity>[^|]*)\|'
        r'(?P<extension>.*)$'
    ),

    # ── SURICATA / SNORT IDS (EVE JSON line ou texte) ────────────────────────
    # Format texte : [**] [1:2001219:20] ET SCAN Potential SSH Scan [**]
    "suricata_alert": re.compile(
        r'^\[?\*\*\]?\s*\[(?P<gid>\d+):(?P<sid>\d+):(?P<rev>\d+)\]\s+'
        r'(?P<alert_msg>[^\[]+)\s*\[\*\*\]'
        r'(?:.*\[Priority:\s*(?P<priority>\d+)\])?'
        r'(?:.*?(?P<src_ip>[\d.]+):?(?P<src_port>\d+)?\s*->\s*(?P<dst_ip>[\d.]+):?(?P<dst_port>\d+)?)?'
    ),

    # ── WAZUH (format JSON log line) ─────────────────────────────────────────
    # Ex: {"timestamp":"2026-01-05T06:25:14","rule":{"id":"5710","level":8},...}
    "wazuh_json": re.compile(
        r'"timestamp"\s*:\s*"(?P<timestamp>[^"]+)".*?'
        r'"id"\s*:\s*"(?P<rule_id>[^"]+)".*?'
        r'"level"\s*:\s*(?P<level>\d+).*?'
        r'"description"\s*:\s*"(?P<description>[^"]+)"',
        re.DOTALL
    ),

    # ── FAIL2BAN ─────────────────────────────────────────────────────────────
    # Ex: 2026-01-05 06:25:14,123 fail2ban.actions[1234]: NOTICE [sshd] Ban 192.168.1.10
    "fail2ban": re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}),\d+\s+'
        r'fail2ban\.\w+\[\d+\]:\s+'
        r'(?P<level>\w+)\s+\[(?P<jail>[\w\-]+)\]\s+'
        r'(?P<action>Ban|Unban|Found|Restore Ban)\s+'
        r'(?P<src_ip>[\d.]+)$'
    ),

    # ── MYSQL / MARIADB ERROR LOG ─────────────────────────────────────────────
    # Ex: 2026-01-05T06:25:14.123456Z 3 [Warning] Access denied for user 'root'@'10.0.0.1'
    "mysql_error": re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+'
        r'(?P<thread_id>\d+)\s+\[(?P<level>\w+)\]\s+'
        r'(?P<message>.+)$'
    ),

    # ── POSTGRESQL ───────────────────────────────────────────────────────────
    # Ex: 2026-01-05 06:25:14 UTC [1234] postgres@mydb FATAL: password authentication failed
    "postgresql": re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+\w+\s+'
        r'\[(?P<pid>\d+)\]\s+'
        r'(?P<user>[\w_.\-@]+)@(?P<db>[\w_.\-]+)\s+'
        r'(?P<level>LOG|ERROR|FATAL|WARNING|NOTICE|DEBUG|INFO):\s+'
        r'(?P<message>.+)$'
    ),

    # ── OPENVPN ──────────────────────────────────────────────────────────────
    # Ex: Mon Jan  5 06:25:14 2026 192.168.1.10:51234 TLS: Initial packet from
    "openvpn": re.compile(
        r'^(?P<timestamp>\w{3}\s+\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4})\s+'
        r'(?P<src_ip>[\d.]+):(?P<src_port>\d+)\s+'
        r'(?P<message>.+)$'
    ),

    # ── WIREGUARD ────────────────────────────────────────────────────────────
    # Ex: Jan  5 06:25:14 server wg-quick[1234]: Peer 1.2.3.4 connected
    "wireguard": re.compile(
        r'^(?P<timestamp>\w{3}\s{1,2}\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<host>[\w.\-]+)\s+wg[^\[]*\[\d+\]:\s+'
        r'(?P<message>.+)$'
    ),

    # ── DHCP (ISC DHCP Server) ───────────────────────────────────────────────
    # Ex: Jan  5 06:25:14 server dhcpd: DHCPREQUEST for 192.168.1.10 from aa:bb:cc:dd:ee:ff
    "dhcp": re.compile(
        r'^(?P<timestamp>\w{3}\s{1,2}\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<host>[\w.\-]+)\s+dhcpd:\s+'
        r'(?P<action>DHCP\w+)\s+for\s+(?P<ip>[\d.]+)\s+'
        r'from\s+(?P<mac>[\w:]+)'
        r'(?:\s+\((?P<hostname>[\w.\-]+)\))?'
    ),

    # ── DNS BIND9 ────────────────────────────────────────────────────────────
    # Ex: 05-Jan-2026 06:25:14.123 client 192.168.1.10#51234: query: google.com IN A
    "dns_bind9": re.compile(
        r'^(?P<timestamp>\d{2}-\w{3}-\d{4}\s+\d{2}:\d{2}:\d{2}\.\d+)\s+'
        r'client\s+(?P<src_ip>[\d.]+)#(?P<src_port>\d+):\s+'
        r'(?P<action>query|response):\s+'
        r'(?P<domain>[\w.\-]+)\s+IN\s+(?P<qtype>\w+)'
    ),

    # ── DOCKER ───────────────────────────────────────────────────────────────
    # Ex: time="2026-01-05T06:25:14Z" level=warning msg="Container exited" container=abc123
    "docker": re.compile(
        r'time="(?P<timestamp>[^"]+)"\s+'
        r'level=(?P<level>\w+)\s+'
        r'msg="(?P<message>[^"]+)"'
        r'(?:\s+container=(?P<container>\w+))?'
        r'(?:\s+image=(?P<image>[\w:.\-/]+))?'
    ),

    # ── KUBERNETES ───────────────────────────────────────────────────────────
    # Ex: I0105 06:25:14.123456 1 controller.go:100] "Starting controller" logger="controller"
    "kubernetes": re.compile(
        r'^(?P<level>[IWEF])(?P<timestamp>\d{4}\s+\d{2}:\d{2}:\d{2}\.\d+)\s+'
        r'(?P<thread>\d+)\s+(?P<source>[\w.\-]+:\d+)\]\s+'
        r'"(?P<message>[^"]+)"'
        r'(?P<extra>.*)$'
    ),

    # ── JSON GÉNÉRIQUE ───────────────────────────────────────────────────────
    # Pour tout log structuré en JSON sur une seule ligne
    "json_generic": re.compile(
        r'^\{.*"(?:timestamp|time|@timestamp|date)"\s*:\s*"(?P<timestamp>[^"]+)".*\}$',
        re.DOTALL
    ),

    # ── PFSENSE FIREWALL (filterlog) ─────────────────────────────────────────

    "pfsense_filterlog": re.compile(
    r'^(?P<timestamp>\w{3}\s{1,2}\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
    r'\S+\s+filterlog:\s+'
    r'\d+,,,\d+,(?P<iface>\w+),\w+,(?P<action>\w+),\w+,\d+,'  # rule,iface,action
    r'[^,]*,[^,]*,[^,]*,[^,]*,\d+,(?P<proto>\w+),\d+,'
    r'(?P<src_ip>[\d.]+),(?P<dst_ip>[\d.]+),'
    r'(?P<src_port>\d+),(?P<dst_port>\d+)'
    r'(?:,.*)?$'
    ),

    # ── OPENVPN (format ISO) ────────────────────────────────────────────────
    "openvpn_iso": re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'
    r'(?:\s+us=\d+)?\s+(?P<message>.+)$'
    ),

    # ── MYSQL / MARIADB GENERAL LOG ─────────────────────────────────────────

    "mysql_general": re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+'
    r'(?P<thread_id>\d+)\s+(?P<command>Query|Connect|Quit|Init DB)\s*'
    r'(?P<message>.*)$'
    ),


    # ── WINDOWS EVENT LOG (format texte exporté) ─────────────────────────────

    "windows_event_text": re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
    r'(?P<source>[\w\s]+?)\s+Event\s+ID:\s+(?P<event_id>\d+)\s+'
    r'(?P<message>.+)$'
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. TABLES DE CORRESPONDANCE POUR L'ENRICHISSEMENT
# ─────────────────────────────────────────────────────────────────────────────

# Windows Event IDs → signification sécurité
WINDOWS_EVENT_SEVERITY = {
    "4624": ("INFO",    "Connexion réussie"),
    "4625": ("HIGH",    "Échec de connexion"),
    "4648": ("MEDIUM",  "Tentative de connexion avec credentials explicites"),
    "4720": ("HIGH",    "Création de compte utilisateur"),
    "4726": ("HIGH",    "Suppression de compte utilisateur"),
    "4728": ("HIGH",    "Membre ajouté à un groupe de sécurité global"),
    "4732": ("HIGH",    "Membre ajouté à un groupe local"),
    "4756": ("HIGH",    "Membre ajouté à un groupe universel"),
    "4740": ("CRITICAL","Compte utilisateur verrouillé"),
    "4767": ("HIGH",    "Compte utilisateur déverrouillé"),
    "4776": ("MEDIUM",  "Validation credentials NTLM"),
    "4771": ("HIGH",    "Échec pré-authentification Kerberos"),
    "4698": ("CRITICAL","Tâche planifiée créée"),
    "7045": ("CRITICAL","Service installé sur le système"),
    "1102": ("CRITICAL","Journal d'audit effacé"),
}

# Wazuh rule levels → sévérité SIEM
WAZUH_LEVEL_MAP = {
    range(0, 4):   "LOW",
    range(4, 8):   "MEDIUM",
    range(8, 12):  "HIGH",
    range(12, 16): "CRITICAL",
}

# Ports sensibles → classification
SENSITIVE_PORTS = {
    "22": "SSH", "23": "Telnet", "25": "SMTP", "53": "DNS",
    "80": "HTTP", "110": "POP3", "143": "IMAP", "443": "HTTPS",
    "445": "SMB", "1433": "MSSQL", "1521": "Oracle", "3306": "MySQL",
    "3389": "RDP", "5432": "PostgreSQL", "5900": "VNC", "6379": "Redis",
    "8080": "HTTP-Alt", "8443": "HTTPS-Alt", "27017": "MongoDB",
}

# ── Éléments génériques utilisés par la catégorisation heuristique ──────────
GENERIC_IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
GENERIC_PORT_REGEX = re.compile(r'\bport[=:\s]+(\d{1,5})\b', re.IGNORECASE)
GENERIC_TIMESTAMP_REGEXES = [
    re.compile(r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?'),
    re.compile(r'\w{3}\s{1,2}\d{1,2}\s+\d{2}:\d{2}:\d{2}'),
    re.compile(r'\d{2}/\d{2}/\d{4}[ T]\d{2}:\d{2}:\d{2}'),
]

# ── Table de catégorisation heuristique (mots-clés → log_type / sévérité) ────
# Utilisée uniquement quand AUCUNE regex stricte de REGEX_PATTERNS n'a matché.
# On explore la ligne brute à la recherche d'éléments caractéristiques connus
# (vocabulaire d'authentification, de pare-feu, d'IDS, de bases de données...)
# pour affecter malgré tout un log_type et une sévérité pertinents plutôt que
# de se rabattre systématiquement sur "inconnu".
# Format de chaque règle : (log_type, sévérité_par_défaut, [mots-clés déclencheurs])
# L'ordre est important : du plus spécifique/critique au plus générique.
HEURISTIC_RULES = [
    ("auth",       "HIGH",     ["failed password", "invalid user", "authentication failure",
                                 "auth fail", "login failed", "échec de connexion",
                                 "access denied", "unauthorized", "authentification échouée"]),
    ("auth",       "NOTICE",   ["accepted password", "accepted publickey", "session opened",
                                 "logon success", "logged in", "connexion réussie"]),
    ("windows",    "HIGH",     ["eventid", "event id", "levels displayname", "leveldisplayname",
                                 "security-auditing", "microsoft-windows", "winevt", "evtx"]),
    ("ids/ips",    "HIGH",     ["alert", "signature", "snort", "suricata", "intrusion",
                                 "exploit", "malware", "trojan", "payload"]),
    ("firewall",   "HIGH",     ["drop", "block", "deny", "reject", "iptables", "netfilter",
                                 "ufw", "firewall"]),
    ("database",   "MEDIUM",   ["mysql", "postgres", "postgresql", "mariadb", "select ",
                                 "insert into", "sql error", "database error", "sqlstate"]),
    ("web",        "MEDIUM",   ["get /", "post /", "put /", "delete /", "http/1.",
                                 "user-agent", " 404 ", " 500 ", "wp-admin", "phpinfo"]),
    ("dns",        "INFO",     ["dns", "query:", " in a\n", " in a ", " in aaaa", "resolver"]),
    ("dhcp",       "INFO",     ["dhcp", "dhcprequest", "dhcpoffer", "dhcpack", "dhcpdiscover"]),
    ("vpn",        "INFO",     ["openvpn", "wireguard", "tls:", "vpn", "ipsec"]),
    ("container",  "INFO",     ["docker", "container", "kubernetes", "k8s", "pod/", "namespace"]),
    ("système",    "MEDIUM",   ["kernel panic", "segfault", "out of memory", "oom-killer",
                                 "service failed", "systemd"]),
    ("réseau",     "NOTICE",   ["tcp", "udp", "icmp", "src=", "dst=", "srcip", "dstip"]),
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. FONCTIONS D'ENRICHISSEMENT
# ─────────────────────────────────────────────────────────────────────────────

def get_wazuh_severity(level: int) -> str:
    for r, sev in WAZUH_LEVEL_MAP.items():
        if level in r:
            return sev
    return "CRITICAL"

def detect_port_sensitivity(port: Optional[str], msg: str = "") -> str:
    """Retourne le service associé à un port, ou détecte depuis le message."""
    if port and port in SENSITIVE_PORTS:
        return SENSITIVE_PORTS[port]
    for p, service in SENSITIVE_PORTS.items():
        if p in msg:
            return service
    return "UNKNOWN"

def parse_cef_extension(ext: str) -> Dict:
    """Parse les champs key=value du bloc extension CEF."""
    result = {}
    for match in re.finditer(r'(\w+)=((?:[^=\\]|\\.)*)(?=\s+\w+=|$)', ext):
        result[match.group(1)] = match.group(2).strip()
    return result

def parse_timestamp(ts_str: str, fmt: str = None) -> datetime:
    """Essaie plusieurs formats de timestamp, retourne utcnow() en dernier recours."""
    formats = [
        fmt,
        "%b %d %H:%M:%S", "%b  %d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S", "%d/%b/%Y:%H:%M:%S %z",
        "%Y/%m/%d,%H:%M:%S", "%Y/%m/%d %H:%M:%S",
        "%d-%b-%Y %H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S%z",
        "%a %b %d %H:%M:%S %Y",
        "%I%m%d %H:%M:%S.%f",
    ]
    for fmt_try in formats:
        if not fmt_try:
            continue
        try:
            dt = datetime.strptime(ts_str.strip(), fmt_try)
            if dt.year == 1900:
                dt = dt.replace(year=2026)
            return dt
        except Exception:
            continue
    return datetime.utcnow()


def heuristic_categorize(raw_line: str) -> Optional[Dict]:
    """
    Catégorisation de secours par mots-clés / éléments caractéristiques.

    Appelée uniquement quand AUCUNE regex de REGEX_PATTERNS n'a matché la ligne.
    Plutôt que de renvoyer immédiatement "inconnu", on cherche dans le texte brut
    des indices connus (vocabulaire d'authentification, de pare-feu, d'IDS, de
    bases de données, adresses IP, ports...) pour affecter un log_type et une
    sévérité aussi précis que possible.

    Retourne None seulement si absolument aucun indice exploitable n'a été trouvé
    (dans ce cas, parse_raw_log se rabat sur le vrai fallback "inconnu").
    """
    text = raw_line.lower()

    matched_type = None
    matched_severity = None
    matched_keyword = None

    for log_type, severity, keywords in HEURISTIC_RULES:
        for kw in keywords:
            if kw in text:
                matched_type = log_type
                matched_severity = severity
                matched_keyword = kw
                break
        if matched_type:
            break

    # Extraction générique d'IP (on garde la 1ère comme source, la 2e comme destination)
    ips = GENERIC_IP_REGEX.findall(raw_line)
    src_ip = ips[0] if len(ips) >= 1 else None
    dst_ip = ips[1] if len(ips) >= 2 else None

    # Extraction générique de port + escalade de sévérité si port sensible touché
    port_match = GENERIC_PORT_REGEX.search(raw_line)
    port = port_match.group(1) if port_match else None
    service = detect_port_sensitivity(port, raw_line) if port else None
    if port in ["22", "3389", "445", "23"] and matched_severity in ["HIGH", "MEDIUM"]:
        matched_severity = "CRITICAL"

    # Extraction générique d'un timestamp si un pattern connu apparaît dans la ligne
    ts_value = None
    for ts_regex in GENERIC_TIMESTAMP_REGEXES:
        ts_m = ts_regex.search(raw_line)
        if ts_m:
            ts_value = ts_m.group(0)
            break
    timestamp = parse_timestamp(ts_value) if ts_value else datetime.utcnow()

    # Aucun mot-clé ET aucune IP détectée : on n'a vraiment rien à proposer
    if not matched_type and not ips:
        return None

    # Une IP a été trouvée mais aucun mot-clé de catégorie : on classe en "réseau"
    # générique plutôt que de perdre l'information, avec une sévérité prudente.
    if not matched_type:
        matched_type = "réseau"
        matched_severity = "NOTICE"
        matched_keyword = "ip_detectee"

    return create_siem_document(
        timestamp=timestamp,
        host="unknown-device", log_type=matched_type, severity=matched_severity,
        source_ip=src_ip, destination_ip=dst_ip, raw_message=raw_line,
        extra={
            "format": "heuristique",
            "matched_keyword": matched_keyword,
            "port": port, "service": service,
        }
    )

# ─────────────────────────────────────────────────────────────────────────────
# 4. PARSERS PAR FORMAT
# ─────────────────────────────────────────────────────────────────────────────

SSH_IP_REGEX = re.compile(r'from\s+([\d.]+)')

def _parse_linux_syslog(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    msg = d["message"]
    process = d.get("process", "")
    log_type = "auth" if any(x in process for x in ["sshd", "sudo", "su", "pam"]) else "système"
    severity = "INFO"
    src_ip = None

    # Détection SSH brute-force / invalid user
    if "Failed password" in msg or "Invalid user" in msg or "authentication failure" in msg:
        severity = "HIGH"
        ip_match = SSH_IP_REGEX.search(msg)
        if ip_match:
            src_ip = ip_match.group(1)
    elif "Accepted password" in msg or "Accepted publickey" in msg:
        severity = "NOTICE"
        ip_match = SSH_IP_REGEX.search(msg)
        if ip_match:
            src_ip = ip_match.group(1)
    elif "sudo" in process and "COMMAND" in msg:
        severity = "MEDIUM"
    elif "segfault" in msg or "kernel panic" in msg:
        severity = "CRITICAL"
        log_type = "système"

    return create_siem_document(
        timestamp=parse_timestamp(d["timestamp"]),
        host=d["host"], log_type=log_type, severity=severity,
        source_ip=src_ip, destination_ip=None,
        raw_message=raw, extra={
            "process": process, "pid": d.get("pid"),
            "message": msg, "format": "linux_syslog"
        }
    )

def _parse_syslog_rfc5424(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    priority = int(d.get("priority", 0))
    severity_map = {0: "CRITICAL", 1: "CRITICAL", 2: "CRITICAL",
                    3: "HIGH", 4: "MEDIUM", 5: "NOTICE", 6: "INFO", 7: "LOW"}
    sev = severity_map.get(priority % 8, "INFO")
    return create_siem_document(
        timestamp=parse_timestamp(d["timestamp"]),
        host=d["host"], log_type="syslog", severity=sev,
        source_ip=None, destination_ip=None, raw_message=raw,
        extra={"app": d.get("app"), "pid": d.get("pid"),
               "msgid": d.get("msgid"), "message": d.get("message"),
               "format": "syslog_rfc5424"}
    )

def _parse_cisco_ios(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    msg = d.get("message", "")
    level = int(d.get("level", 6))
    sev_map = {0:"CRITICAL",1:"CRITICAL",2:"CRITICAL",3:"HIGH",
               4:"MEDIUM",5:"NOTICE",6:"INFO",7:"LOW"}
    sev = sev_map.get(level, "INFO")

    # Extraire user et source IP depuis le message
    user_m = re.search(r'\[user:\s*([\w@.\-]+)\]', msg)
    src_m  = re.search(r'\[Source:\s*([\d.]+)\]', msg)

    mnemonic = d.get("mnemonic", "")
    if "FAIL" in mnemonic or "DENIED" in mnemonic:
        sev = "HIGH"

    return create_siem_document(
        timestamp=parse_timestamp(d["timestamp"]),
        host=d["host"], log_type="network", severity=sev,
        source_ip=src_m.group(1) if src_m else None,
        destination_ip=None, raw_message=raw,
        extra={
            "facility": d.get("facility"),
            "mnemonic": mnemonic,
            "user": user_m.group(1) if user_m else None,
            "message": msg,
            "format": "cisco_ios"
        }
    )

def _parse_apache_nginx(raw: str, m: re.Match, fmt: str) -> Dict:
    d = m.groupdict()
    status = int(d.get("status", 200))
    method = d.get("method", "")
    path = d.get("path", "")
    severity = "INFO"
    if status >= 500:
        severity = "HIGH"
    elif status >= 400:
        severity = "MEDIUM"
    # Détection d'attaques web basiques
    suspicious = ["..", "etc/passwd", "cmd=", "exec(", "<script", "UNION SELECT",
                  "wp-admin", ".php?", "phpinfo", "eval(", "base64_decode"]
    if any(s.lower() in path.lower() for s in suspicious):
        severity = "HIGH"
    return create_siem_document(
        timestamp=parse_timestamp(d.get("timestamp", ""), "%d/%b/%Y:%H:%M:%S %z"),
        host="web-server", log_type="web", severity=severity,
        source_ip=d.get("src_ip"), destination_ip=None, raw_message=raw,
        extra={"method": method, "path": path, "status": status,
               "user_agent": d.get("user_agent"), "format": fmt}
    )

def _parse_windows_event(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    event_id = d.get("event_id", "0")
    sev, desc = WINDOWS_EVENT_SEVERITY.get(event_id, ("INFO", "Événement Windows"))
    return create_siem_document(
        timestamp=parse_timestamp(d.get("timestamp", "")),
        host=d.get("computer", "windows-host"), log_type="windows", severity=sev,
        source_ip=None, destination_ip=None, raw_message=raw,
        extra={"event_id": event_id, "event_desc": desc,
               "user": d.get("user"), "source": d.get("source"),
               "message": d.get("message", ""), "format": "windows_event"}
    )

def _parse_iptables(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    action = (d.get("action") or "").strip().upper()
    severity = "HIGH" if "BLOCK" in action or "DROP" in action or "DENY" in action else "NOTICE"
    dst_port = d.get("dst_port")
    service = detect_port_sensitivity(dst_port)
    if dst_port in ["22", "3389", "445"] and severity == "HIGH":
        severity = "CRITICAL"
    return create_siem_document(
        timestamp=parse_timestamp(d.get("timestamp", "")),
        host=d.get("host", "firewall"), log_type="firewall", severity=severity,
        source_ip=d.get("src_ip"), destination_ip=d.get("dst_ip"), raw_message=raw,
        extra={"action": action, "proto": d.get("proto"),
               "src_port": d.get("src_port"), "dst_port": dst_port,
               "service": service, "in_iface": d.get("in_iface"),
               "out_iface": d.get("out_iface"), "format": "iptables"}
    )

def _parse_cisco_asa(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    level = int(d.get("level", 6))
    sev_map = {1: "CRITICAL", 2: "CRITICAL", 3: "HIGH",
               4: "MEDIUM", 5: "NOTICE", 6: "INFO", 7: "LOW"}
    sev = sev_map.get(level, "INFO")
    return create_siem_document(
        timestamp=datetime.utcnow(),
        host="cisco-asa", log_type="firewall", severity=sev,
        source_ip=d.get("src_ip"), destination_ip=d.get("dst_ip"), raw_message=raw,
        extra={"msg_id": d.get("msg_id"), "action": d.get("action"),
               "proto": d.get("proto"), "src_port": d.get("src_port"),
               "dst_port": d.get("dst_port"), "format": "cisco_asa"}
    )

def _parse_cef(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    ext = parse_cef_extension(d.get("extension", ""))
    sev_raw = d.get("severity", "5")
    try:
        sev_int = int(sev_raw)
        sev = "LOW" if sev_int < 3 else "MEDIUM" if sev_int < 6 else "HIGH" if sev_int < 9 else "CRITICAL"
    except Exception:
        sev = "INFO"
    return create_siem_document(
        timestamp=parse_timestamp(ext.get("rt", ext.get("deviceReceiptTime", ""))),
        host=ext.get("dvc", "cef-device"), log_type="ids/ips", severity=sev,
        source_ip=ext.get("src"), destination_ip=ext.get("dst"), raw_message=raw,
        extra={"vendor": d.get("device_vendor"), "product": d.get("device_product"),
               "signature": d.get("signature_id"), "name": d.get("name"),
               "extension": ext, "format": "cef"}
    )

def _parse_suricata(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    priority = int(d.get("priority", 2) or 2)
    sev = "CRITICAL" if priority == 1 else "HIGH" if priority == 2 else "MEDIUM"
    return create_siem_document(
        timestamp=datetime.utcnow(),
        host="ids-sensor", log_type="ids/ips", severity=sev,
        source_ip=d.get("src_ip"), destination_ip=d.get("dst_ip"), raw_message=raw,
        extra={"sid": d.get("sid"), "gid": d.get("gid"), "rev": d.get("rev"),
               "alert": d.get("alert_msg"), "src_port": d.get("src_port"),
               "dst_port": d.get("dst_port"), "format": "suricata"}
    )

def _parse_wazuh(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    level = int(d.get("level", 0))
    sev = get_wazuh_severity(level)
    return create_siem_document(
        timestamp=parse_timestamp(d.get("timestamp", "")),
        host="wazuh-agent", log_type="wazuh", severity=sev,
        source_ip=None, destination_ip=None, raw_message=raw,
        extra={"rule_id": d.get("rule_id"), "level": level,
               "description": d.get("description"), "format": "wazuh"}
    )

def _parse_fail2ban(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    action = d.get("action", "")
    sev = "HIGH" if "Ban" in action else "NOTICE"
    return create_siem_document(
        timestamp=parse_timestamp(d.get("timestamp", ""), "%Y-%m-%d %H:%M:%S"),
        host="fail2ban-host", log_type="fail2ban", severity=sev,
        source_ip=d.get("src_ip"), destination_ip=None, raw_message=raw,
        extra={"jail": d.get("jail"), "action": action, "format": "fail2ban"}
    )

def _parse_db_log(raw: str, m: re.Match, fmt: str) -> Dict:
    d = m.groupdict()
    level_raw = (d.get("level") or "").upper()
    sev = "CRITICAL" if level_raw in ["FATAL", "ERROR"] else \
          "MEDIUM"   if level_raw in ["WARNING", "WARN"] else "INFO"
    msg = d.get("message", "")
    if "Access denied" in msg or "authentication failed" in msg:
        sev = "HIGH"
    return create_siem_document(
        timestamp=parse_timestamp(d.get("timestamp", "")),
        host=d.get("host", "db-server"), log_type="database", severity=sev,
        source_ip=None, destination_ip=None, raw_message=raw,
        extra={"db_level": level_raw, "message": msg,
               "user": d.get("user"), "db": d.get("db"), "format": fmt}
    )

def _parse_openvpn(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    msg = d.get("message", "")
    sev = "HIGH" if "TLS Error" in msg or "AUTH_FAILED" in msg else \
          "NOTICE" if "peer info" in msg.lower() else "INFO"
    return create_siem_document(
        timestamp=parse_timestamp(d.get("timestamp", ""), "%a %b  %d %H:%M:%S %Y"),
        host="vpn-server", log_type="vpn", severity=sev,
        source_ip=d.get("src_ip"), destination_ip=None, raw_message=raw,
        extra={"src_port": d.get("src_port"), "message": msg, "format": "openvpn"}
    )

def _parse_dhcp(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    return create_siem_document(
        timestamp=parse_timestamp(d.get("timestamp", "")),
        host=d.get("host", "dhcp-server"), log_type="dhcp", severity="INFO",
        source_ip=None, destination_ip=d.get("ip"), raw_message=raw,
        extra={"action": d.get("action"), "mac": d.get("mac"),
               "hostname": d.get("hostname"), "format": "dhcp"}
    )

def _parse_dns(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    domain = d.get("domain", "")
    sev = "INFO"
    suspicious_tlds = [".ru", ".cn", ".tk", ".xyz", ".top"]
    if any(domain.endswith(t) for t in suspicious_tlds):
        sev = "MEDIUM"
    return create_siem_document(
        timestamp=parse_timestamp(d.get("timestamp", ""), "%d-%b-%Y %H:%M:%S.%f"),
        host="dns-server", log_type="dns", severity=sev,
        source_ip=d.get("src_ip"), destination_ip=None, raw_message=raw,
        extra={"domain": domain, "qtype": d.get("qtype"),
               "action": d.get("action"), "format": "dns_bind9"}
    )

def _parse_docker(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    level = (d.get("level") or "info").lower()
    sev = "HIGH" if level == "error" else "MEDIUM" if level == "warning" else "INFO"
    return create_siem_document(
        timestamp=parse_timestamp(d.get("timestamp", "")),
        host="docker-host", log_type="container", severity=sev,
        source_ip=None, destination_ip=None, raw_message=raw,
        extra={"container": d.get("container"), "image": d.get("image"),
               "message": d.get("message"), "format": "docker"}
    )

def _parse_kubernetes(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    lvl = d.get("level", "I")
    sev = {"I": "INFO", "W": "MEDIUM", "E": "HIGH", "F": "CRITICAL"}.get(lvl, "INFO")
    ts_str = d.get("timestamp", "")
    # Format Kubernetes : MMDD HH:MM:SS.ffffff
    try:
        now = datetime.utcnow()
        ts = datetime.strptime(f"{now.year}{ts_str}", "%Y%m%d %H:%M:%S.%f")
    except Exception:
        ts = datetime.utcnow()
    return create_siem_document(
        timestamp=ts, host="k8s-node", log_type="kubernetes", severity=sev,
        source_ip=None, destination_ip=None, raw_message=raw,
        extra={"source": d.get("source"), "message": d.get("message"),
               "thread": d.get("thread"), "format": "kubernetes"}
    )

def _parse_wireshark(raw: str, m: re.Match) -> Dict:
    d = m.groupdict()
    msg = d.get("msg", "")
    dst_port = re.search(r'Dst Port:\s*(\d+)|:(\d+)\s*$', msg)
    dst_port_str = (dst_port.group(1) or dst_port.group(2)) if dst_port else None
    service = detect_port_sensitivity(dst_port_str, msg)
    sev = "NOTICE"
    if dst_port_str in ["22", "3389", "445", "23"]:
        sev = "MEDIUM"
    return create_siem_document(
        timestamp=datetime.utcnow(),
        host="network-capture", log_type="réseau", severity=sev,
        source_ip=d.get("src_ip"), destination_ip=d.get("dst_ip"), raw_message=raw,
        extra={"proto": d.get("proto"), "len": d.get("len"),
               "service": service, "message": msg, "format": "wireshark"}
    )

# ─────────────────────────────────────────────────────────────────────────────
# 5. FONCTION PRINCIPALE : parse_raw_log
# ─────────────────────────────────────────────────────────────────────────────

# Ordre de priorité : du plus spécifique au plus générique
PARSER_PIPELINE = [
    ("wazuh_json",      _parse_wazuh),
    ("cef",             _parse_cef),
    ("suricata_alert",  _parse_suricata),
    ("fail2ban",        _parse_fail2ban),
    ("cisco_asa",       _parse_cisco_asa),
    ("palo_alto",       None),
    ("windows_event",   _parse_windows_event),
    ("postgresql",      lambda r, m: _parse_db_log(r, m, "postgresql")),
    ("mysql_error",     lambda r, m: _parse_db_log(r, m, "mysql")),
    ("apache_access",   lambda r, m: _parse_apache_nginx(r, m, "apache")),
    ("nginx_access",    lambda r, m: _parse_apache_nginx(r, m, "nginx")),
    ("nginx_error",     lambda r, m: _parse_apache_nginx(r, m, "nginx_error")),
    ("openvpn",         _parse_openvpn),
    ("cisco_ios",       _parse_cisco_ios),
    ("linux_syslog", _parse_linux_syslog),
    ("wireguard",       lambda r, m: _parse_linux_syslog(r, m)),
    ("dhcp",            _parse_dhcp),
    ("dns_bind9",       _parse_dns),
    ("docker",          _parse_docker),
    ("kubernetes",      _parse_kubernetes),
    ("syslog_rfc5424",  _parse_syslog_rfc5424),
    ("linux_syslog",    _parse_linux_syslog),   # ← APRÈS les patterns spécifiques
    ("wireshark",       _parse_wireshark),
    # iptables EN DERNIER parmi les syslog-like
    ("iptables",        _parse_iptables),
]

def parse_raw_log(raw_line: str) -> Dict:
    """
    Parser universel Smart SIEM.
    Détecte automatiquement le format du log et retourne
    un document normalisé au format dictionnaire de données SIEM.
    """
    raw_line = raw_line.strip()

    # Tentative JSON générique en premier si la ligne commence par {
    if raw_line.startswith("{"):
        try:
            import json
            obj = json.loads(raw_line)

            # 🟢 Cas particulier : JSON d'événement Windows tel que produit par
            # `Get-WinEvent | ConvertTo-Json` côté agent (champs PowerShell natifs
            # Id / EventID, LevelDisplayName, ProviderName, TimeCreated, MachineName,
            # RecordId, Message). Sans cette détection, ces logs étaient auparavant
            # catégorisés en "json" générique au lieu de "windows".
            event_id = str(obj.get("Id", obj.get("EventID", obj.get("event_id", ""))))
            is_windows_event = bool(event_id) and (
                "LevelDisplayName" in obj or "ProviderName" in obj
                or "MachineName" in obj or "RecordId" in obj
            )
            if is_windows_event:
                sev, desc = WINDOWS_EVENT_SEVERITY.get(event_id, ("INFO", "Événement Windows"))
                ts_raw = obj.get("TimeCreated", obj.get("timestamp"))
                ts = parse_timestamp(str(ts_raw)) if ts_raw else datetime.utcnow()
                return create_siem_document(
                    timestamp=ts,
                    host=obj.get("MachineName", "windows-host"),
                    log_type="windows", severity=sev,
                    source_ip=None, destination_ip=None, raw_message=raw_line,
                    extra={
                        "format": "windows_event_json", "event_id": event_id,
                        "event_desc": desc,
                        "provider": obj.get("ProviderName"),
                        "level": obj.get("LevelDisplayName"),
                        "user": obj.get("UserId", obj.get("user")),
                        "message": obj.get("Message"),
                        "record_id": obj.get("RecordId"),
                    }
                )

            ts_key = next((k for k in ["timestamp","time","@timestamp","date","TimeCreated"] if k in obj), None)
            ts = parse_timestamp(str(obj[ts_key])) if ts_key else datetime.utcnow()
            sev = str(obj.get("level", obj.get("severity", "INFO"))).upper()
            sev = sev if sev in ["LOW","INFO","NOTICE","MEDIUM","HIGH","CRITICAL"] else "INFO"
            return create_siem_document(
                timestamp=ts,
                host=obj.get("host", obj.get("hostname", obj.get("agent", {}).get("hostname", "json-host"))),
                log_type=obj.get("log_type", obj.get("type", "json")),
                severity=sev,
                source_ip=obj.get("src_ip", obj.get("source_ip", obj.get("srcip"))),
                destination_ip=obj.get("dst_ip", obj.get("destination_ip", obj.get("dstip"))),
                raw_message=raw_line,
                extra={"format": "json_generic", "parsed_fields": obj}
            )
        except Exception:
            pass

    # Pipeline séquentiel
    for format_name, handler in PARSER_PIPELINE:
        pattern = REGEX_PATTERNS.get(format_name)
        if not pattern:
            continue
        m = pattern.search(raw_line)
        if m and handler:
            return handler(raw_line, m)

    # 🟢 Catégorisation heuristique de secours : avant de déclarer le log
    # "inconnu", on tente de le catégoriser à partir de mots-clés et d'éléments
    # caractéristiques (IP, ports, vocabulaire sécurité) présents dans la ligne.
    # C'est ce qui évite qu'un format légèrement différent d'une regex stricte
    # (espacement, variante de champ, etc.) finisse systématiquement en "inconnu".
    heuristic_result = heuristic_categorize(raw_line)
    if heuristic_result:
        return heuristic_result

    # Fallback ultime : log réellement non identifiable — on ne perd rien
    return create_siem_document(
        timestamp=datetime.utcnow(),
        host="unknown-device", log_type="inconnu", severity="LOW",
        source_ip=None, destination_ip=None, raw_message=raw_line,
        extra={"format": "unknown"}
    )


def parse_log_batch(lines: List[str]) -> List[Dict]:
    """Parse une liste de lignes brutes en lot."""
    return [parse_raw_log(line) for line in lines if line.strip()]


# ─────────────────────────────────────────────────────────────────────────────
# 6. HELPER : create_siem_document
# ─────────────────────────────────────────────────────────────────────────────

def create_siem_document(timestamp, host, log_type, severity,
                          source_ip, destination_ip, raw_message,
                          extra: Optional[Dict] = None) -> Dict:
    """Standardise la sortie au format dictionnaire de données SIEM."""

    if isinstance(timestamp, str):
        try:
            # Tente de parser le format ISO standard si c'est du texte
            final_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except Exception:
            final_timestamp = datetime.utcnow()
    else:
        final_timestamp = timestamp if timestamp else datetime.utcnow()

    return {
        "id":               f"LOG-{uuid.uuid4().hex[:8].upper()}",
        "timestamp":        final_timestamp,
        "host":             host or "unknown",
        "log_type":         log_type,
        "severity":         severity,
        "source_ip":        source_ip,
        "destination_ip":   destination_ip,
        "raw_message":      raw_message,
        "is_suspect":       severity in ["HIGH", "CRITICAL"],
        "perimetre_id":     "PERIM-01",
        "extra":            extra or {},
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. TESTS D'AUTOVALIDATION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    TEST_LOGS = [
        # Linux Syslog SSH brute-force
        "Jan  5 06:25:14 server01 sshd[12345]: Failed password for root from 192.168.1.10 port 22 ssh2",
        # Linux Syslog connexion réussie
        "Jan  5 06:26:00 server01 sshd[12346]: Accepted publickey for ubuntu from 10.0.0.5 port 51234",
        # Apache access log
        '192.168.1.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 2326 "-" "Mozilla/5.0"',
        # Apache attaque LFI
        '10.0.0.2 - - [05/Jan/2026:06:00:00 +0000] "GET /../../../../etc/passwd HTTP/1.1" 404 512 "-" "curl/7.68"',
        # Nginx error
        "2026/01/05 06:25:14 [error] 1234#1234: *1 connect() failed (111: Connection refused)",
        # Windows Event 4625 (échec connexion)
        "2026-01-05 06:25:14 EventID=4625 Level=Error Source=Security Computer=WS01 User=DOMAIN\\john Message=An account failed to log on",
        # Windows Event 4740 (compte verrouillé)
        "2026-01-05 07:00:00 EventID=4740 Level=Error Source=Security Computer=DC01 User=DOMAIN\\alice Message=Account locked out",
        # iptables DROP
        "Jan  5 06:25:14 fw01 kernel: [UFW BLOCK] IN=eth0 OUT= SRC=192.168.1.99 DST=10.0.0.1 PROTO=TCP SPT=54321 DPT=22",
        # Cisco ASA
        "%ASA-6-302013: Built inbound TCP connection 123 for inside:10.0.0.1/1234 to outside:8.8.8.8/443",
        # CEF
        "CEF:0|Security|IDS|1.0|100|SQL Injection Attempt|8|src=192.168.1.50 dst=10.0.0.10 rt=1704430800000",
        # Suricata IDS
        "[**] [1:2001219:20] ET SCAN Potential SSH Scan [**] [Classification: Misc activity] [Priority: 3] 10.0.0.5:54321 -> 192.168.1.1:22",
        # Fail2ban Ban
        "2026-01-05 06:25:14,123 fail2ban.actions[9999]: NOTICE [sshd] Ban 192.168.1.10",
        # PostgreSQL
        "2026-01-05 06:25:14 UTC [5432] admin@mydb FATAL: password authentication failed for user \"admin\"",
        # OpenVPN
        "Mon Jan  5 06:25:14 2026 192.168.2.100:51234 TLS: Initial packet from [AF_INET]192.168.2.100:51234",
        # DHCP
        "Jan  5 06:25:14 server dhcpd: DHCPREQUEST for 192.168.1.50 from aa:bb:cc:dd:ee:ff (laptop-john)",
        # DNS Bind9
        "05-Jan-2026 06:25:14.123 client 192.168.1.10#51234: query: google.com IN A",
        # Wireshark/Tcpdump
        "1  0.000000  192.168.1.1  8.8.8.8  DNS  72  Standard query A google.com",
        # Docker
        'time="2026-01-05T06:25:14Z" level=error msg="Container exited unexpectedly" container=abc123def image=nginx:latest',
        # Wazuh JSON
        '{"timestamp":"2026-01-05T06:25:14.000Z","rule":{"id":"5710","level":10,"description":"SSH brute force attack detected"},"agent":{"name":"server01"}}',
        # JSON générique
        '{"timestamp":"2026-01-05T08:00:00Z","host":"app-server","level":"ERROR","source_ip":"10.0.0.5","message":"Unauthorized access"}',
        # 🟢 JSON Windows réel (Get-WinEvent | ConvertTo-Json côté agent)
        '{"RecordId":86,"Id":4625,"LevelDisplayName":"Error","ProviderName":"Microsoft-Windows-Security-Auditing","MachineName":"WS01","TimeCreated":"2026-01-05T06:25:14Z","Message":"An account failed to log on."}',
        # 🟢 Variante SSH légèrement différente d'une regex stricte (heuristique)
        "auth: user root failed password attempt from 203.0.113.7 port 22 on server-prod",
        # 🟢 Ligne pare-feu non standard (heuristique)
        "firewall-edge: connection DROP proto TCP src=198.51.100.4 dst=10.0.0.9 port=3389",
        # Log inconnu
        "ZXCV 9999 *** format totalement inconnu *** blabla",
    ]

    print("=" * 72)
    print(" SMART SIEM — TEST DE NORMALISATION UNIVERSELLE")
    print(f" {len(TEST_LOGS)} formats testés")
    print("=" * 72)

    suspects = 0
    for i, log in enumerate(TEST_LOGS, 1):
        result = parse_raw_log(log)
        fmt = result.get("extra", {}).get("format", "?")
        flag = "🔴 SUSPECT" if result["is_suspect"] else "🟢"
        if result["is_suspect"]:
            suspects += 1
        print(f"\n[{i:02d}] {flag}")
        print(f"     Format     : {fmt}")
        print(f"     Type       : {result['log_type']}")
        print(f"     Sévérité   : {result['severity']}")
        print(f"     Host       : {result['host']}")
        print(f"     IP src     : {result['source_ip']}")
        print(f"     IP dst     : {result['destination_ip']}")
        print(f"     Timestamp  : {result['timestamp']}")
        if result.get("extra"):
            extra_display = {k: v for k, v in result["extra"].items()
                             if k not in ["format", "parsed_fields"] and v}
            if extra_display:
                print(f"     Extra      : {json.dumps(extra_display, ensure_ascii=False, default=str)[:120]}")
        print(f"     ID         : {result['id']}")

    print("\n" + "=" * 72)
    print(f" RÉSUMÉ : {len(TEST_LOGS)} logs traités | {suspects} suspects détectés")
    print("=" * 72)