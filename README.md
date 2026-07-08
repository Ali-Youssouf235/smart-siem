# Smart-SIEM Agent

Un agent SIEM **léger**, **multi-OS** et **résilient** qui collecte les logs système en temps réel et les envoie à votre backend d'analyse centralisée.

---

## 🎯 Caractéristiques

✅ **Multi-plateforme** : Linux et Windows  
✅ **Collecte intelligente** : N'envoie que les NOUVEAUX logs (pas de duplication)  
✅ **Résilient** : Cache local en cas de panne du backend  
✅ **Sécurisé** : Demande authentification avant déploiement  
✅ **Configurable** : Configuration YAML simple  
✅ **Léger** : Minimal en ressources CPU/RAM  

---

## 📋 Prérequis

### Sur Linux
- **Python 3.7+**
- **pip** (gestionnaire de paquets Python)
- **Droits sudo** (pour accéder à `/var/log/*`)

### Sur Windows
- **Python 3.7+**
- **pip**
- **Droits Administrateur**
- **PowerShell** (optionnel, pour exécution en arrière-plan)

### Réseau
- Accès à l'API backend (HTTP POST)
- Connectivité vers votre serveur SIEM

---

## 🚀 Installation Rapide

### 1️⃣ Cloner le dépôt
```bash
git clone https://github.com/yourusername/smart-siem.git
cd smart-siem
```

### 2️⃣ Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3️⃣ Configurer l'agent
Lancez l'installateur GUI :
```bash
python installer.py
```

**Sur Linux** :
- Entrez votre mot de passe sudo
- Entrez l'URL du backend (ex: `http://10.237.69.157:8000`)
- Cliquez "Sauvegarder la Configuration"
- Cliquez "Installer et Démarrer l'Agent"

**Sur Windows** :
- Exécutez en tant qu'administrateur (clic droit → "Exécuter en tant qu'administrateur")
- Entrez l'URL du backend
- Cliquez les deux boutons

### ✅ Vérification

Vérifiez que l'agent fonctionne :
```bash
# Linux
ps aux | grep main.py

# Windows
tasklist | findstr python.exe
```

Consulter les logs :
```bash
tail -f agent_start.log
tail -f logs/agent.log
```

---

## 📖 Utilisation

### Lancer manuellement
```bash
python main.py
```

### Arrêter l'agent
```bash
# Linux
sudo pkill -f "main.py"

# Windows
taskkill /F /IM python.exe
```

### Simuler une attaque (test)
```bash
python simulate_attack.py
```

Cela génère des logs d'attaque SSH pour tester la collecte.

---

## 📝 Configuration

Le fichier `config/config.yaml` est généré automatiquement par `installer.py`.

### Format
```yaml
agent:
  name: Smart-SIEM-Agent
  version: 1.0.0
  buffer_max_size: 5000  # Cache max en cas de panne
  perimetre_id: perimetre-dmz

backend:
  url: http://10.237.69.157:8000/api/logs/ingest
  timeout: 10
  retry_interval: 5

logs:
  # Sur Linux
  files:
    - /var/log/syslog
    - /var/log/auth.log
  
  # Sur Windows: utilisé automatiquement
  # source: Windows Event Logs

logging:
  level: INFO
  file: logs/agent.log
```

### Modifier manuellement
Éditez directement `config/config.yaml` si nécessaire.

---

## 🔄 Flux de Collecte

```
Agent détecte l'OS
       ↓
Linux → Lit /var/log/auth.log et /var/log/syslog
Windows → Récupère Security Event Log via wevtutil
       ↓
Parse et normalise
       ↓
Envoie vers API backend
       ↓
Si succès → Enregistre position
Si échec → Stocke en cache local (max 5000 logs)
       ↓
Retry automatique dès que API revient
```

---

## 📊 Modèle de données

Chaque log envoyé à l'API respecte ce format :

```json
{
  "raw_message": "Feb 08 10:30:45 ubuntu sshd[1234]: Failed password for user from 192.168.1.1",
  "host": "ubuntu-server",
  "perimetre_id": "perimetre-dmz"
}
```

---

## 🐛 Dépannage

### Erreur: "config.yaml not found"
→ Relancez `python installer.py`

### Erreur: "Permission denied" (Linux)
→ L'agent nécessite les droits sudo pour accéder aux logs.  
→ Relancez `python installer.py` et authentifiez-vous.

### Erreur: "Access Denied" (Windows)
→ Exécutez `python installer.py` en tant qu'administrateur.  
→ Clic droit → "Exécuter en tant qu'administrateur"

### Pas de logs collectés
→ Vérifiez que les fichiers de log existent:
```bash
# Linux
ls -la /var/log/auth.log
ls -la /var/log/syslog

# Windows
wevtutil qe Security /c:1
```

### API backend ne reçoit rien
→ Vérifiez la connectivité:
```bash
curl -X POST http://YOUR_API/api/logs/ingest \
  -H "Content-Type: application/json" \
  -d '{"raw_message":"test","host":"test","perimetre_id":"test"}'
```

---

## 📂 Structure du Projet

```
smart-siem/
├── README.md                 # Cette documentation
├── requirements.txt          # Dépendances Python
├── main.py                  # Point d'entrée principal
├── installer.py             # Installation GUI (Linux + Windows)
├── simulate_attack.py       # Générateur de logs test
│
├── agent/                   # Code agent SIEM
│   ├── __init__.py
│   ├── collector.py         # Orchestrateur central (détecte OS)
│   ├── config_loader.py     # Charge config.yaml
│   ├── logger.py            # Gestion des logs
│   ├── models.py            # Modèles de données (LogPayload)
│   ├── parser.py            # Normalise les logs
│   ├── sender.py            # Envoie vers API backend
│   ├── retry.py             # Gestion du cache résilient
│   │
│   └── collectors/          # Collecteurs spécifiques par OS
│       ├── base.py          # Classe abstraite
│       ├── linux.py         # Collecteur Linux
│       └── windows.py       # Collecteur Windows
│
├── config/
│   └── config.yaml          # (Généré par installer.py)
│
├── logs/                    # Logs de l'agent
│   └── agent.log
│
└── backend/                 # Placeholder (à implémenter)
    └── Dockerfile
```

---

## 🔐 Sécurité

### Authentification
- **Linux** : Demande mot de passe sudo avant déploiement
- **Windows** : Demande droits administrateur via UAC

### Données sensibles
- `config.yaml` ne doit PAS être committé (voir `.gitignore`)
- Les fichiers d'état (`agent_state_*.json`) sont locaux
- Les logs sont stockés dans `logs/` en lecture locale

### Fichiers ignorés par Git
```
config/config.yaml          # Config locale (sensible)
agent_state_*.json          # État local
logs/                       # Logs locaux
__pycache__/                # Cache Python
*.pyc                       # Bytecode compilé
.env                        # Variables d'environnement
```

---

## 📞 Support

Pour toute question ou bug :
1. Vérifiez le fichier `logs/agent.log`
2. Testez la connectivité réseau
3. Consultez la section Dépannage ci-dessus

---

## 📄 License

MIT - Libre d'utilisation

---

## 🎉 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

---

**Version actuelle** : 1.0.0  
**Dernière mise à jour** : Juillet 2026
