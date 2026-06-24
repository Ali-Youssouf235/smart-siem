# generate_test_data.py
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from pipeline import ingest_log

fake = Faker('fr_FR')

HOSTS = ["srv-web-01", "srv-db-01", "srv-proxy-01", "workstation-15",
         "fw-core-01", "srv-ldap-01", "bastion-ssh"]

PERIMETRES = ["perimetre-dmz", "perimetre-lan", "perimetre-admin"]

# Scénarios pondérés — couvrent les catégories MITRE de ton dictionnaire
SCENARIOS = [
    # (template, poids)
    # Reconnaissance
    ("nmap: SYN scan detected from {ip} on {host} port {port}",           5),
    # Credential Access (brute-force SSH — déclenchera la règle de corrélation)
    ("Failed password for {user} from {ip} port {port} ssh2",             35),
    ("Failed password for invalid user {user} from {ip} port {port} ssh2",15),
    # Lateral Movement
    ("Accepted password for {user} from {ip} port {port} ssh2",           12),
    ("sudo: {user} : TTY=pts/0 ; PWD=/root ; COMMAND=/bin/bash",           5),
    # Defense Evasion
    ("kernel: iptables DROPPED IN=eth0 SRC={ip} DST={dst} PROTO=TCP",     10),
    # Exfiltration
    ("sshd: Disconnecting: {ip}: Too many authentication failures",         8),
    # Normal activity
    ("cron[{pid}]: ({user}) CMD (/usr/bin/backup.sh)",                     5),
    ("systemd[1]: Started Daily apt activities.",                            5),
]

def generate_logs(count: int = 1000):
    now = datetime.now(timezone.utc)
    templates, weights = zip(*SCENARIOS)

    # Générer quelques IPs "attaquantes" qui reviendront souvent
    attacker_ips = [fake.ipv4() for _ in range(5)]

    for i in range(count):
        ts = now - timedelta(
            days=random.uniform(0, 7),
            hours=random.uniform(0, 23),
            minutes=random.uniform(0, 59)
        )

        template = random.choices(templates, weights=weights)[0]

        # Les tentatives de brute-force utilisent les IPs attaquantes
        if "Failed password" in template:
            ip = random.choice(attacker_ips)   # même IP répétée → déclenche la corrélation
        else:
            ip = fake.ipv4()

        message = template.format(
            user=fake.user_name(),
            ip=ip,
            dst=fake.ipv4_private(),
            port=random.randint(1024, 65535),
            pid=random.randint(1000, 9999),
            host=random.choice(HOSTS)
        )

        ingest_log(
            raw_message=message,
            host=random.choice(HOSTS),
            perimetre_id=random.choice(PERIMETRES),
            timestamp=ts
        )

        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{count} logs ingérés...")

    print("✅ Génération terminée !")

if __name__ == "__main__":
    print("Génération de 1000 logs de test...")
    generate_logs(1000)