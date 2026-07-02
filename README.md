# smart-siem
# Smart SIEM — README Technique

Version : 1.0
Auteur : ALI YOUSSOUF (Ingénieur DevOps)
Date : 27/06/2026
Statut : En cours

---

## Table des matières
1. Présentation du projet
2. Prérequis
3. Architecture des services
4. Installation et démarrage
5. Structure du dépôt Git
6. Gestion des secrets
7. À compléter ultérieurement

---

## 1. Présentation du projet

Smart SIEM est une plateforme de gestion et d'analyse des événements de
sécurité (SIEM) développée dans le cadre d'un projet étudiant transversal.
Elle permet à une équipe SOC (Security Operations Center) de centraliser,
normaliser, corréler et visualiser les événements de sécurité issus de
sources hétérogènes.

**Équipe :**
- Chef de projet / Backend
- Développeur Backend
- Développeur Frontend
- Ingénieur Infrastructure
- Ingénieur Data
- Ingénieur DevOps (ALI YOUSSOUF)

---

## 2. Prérequis

Avant de démarrer le projet, les outils suivants doivent être installés
sur la machine :

| Outil | Version recommandée | Utilité |
|---|---|---|
| Docker Desktop | Dernière version stable | Conteneurisation |
| Git | 2.x ou supérieur | Versioning |
| IntelliJ IDEA Ultimate | Dernière version | IDE principal |

---

## 3. Architecture des services

Le projet est composé des services suivants orchestrés via Docker Compose :

| Service | Image | Port | Rôle |
|---|---|---|---|
| backend | Build local (FastAPI) | 8000 | API REST principale |
| frontend | Build local (Node) | 3000 | Interface utilisateur |
| elasticsearch | docker.elastic.co/elasticsearch:8.13.0 | 9200 | Stockage et indexation des logs |
| kibana | docker.elastic.co/kibana:8.13.0 | 5601 | Visualisation Elasticsearch |
| filebeat | docker.elastic.co/beats/filebeat:8.13.0 | — | Agent de collecte de logs |

---

## 4. Installation et démarrage

### Cloner le dépôt
git clone https://github.com/<owner>/smart-siem.git

cd smart-siem

### Configurer les variables d'environnement
Créer un fichier `.env` à la racine du projet avec ce contenu :
ELASTIC_PASSWORD=siem2026

ELASTIC_USERNAME=elastic

ELASTIC_CLUSTER_NAME=siem-cluster

ELASTIC_NODE_NAME=siem-node

KIBANA_SERVICE_ACCOUNT_TOKEN=<token_kibana>

### Démarrer tous les services
docker compose up --build

### Vérifier que tout fonctionne
- Elasticsearch : http://localhost:9200 (login : elastic / siem2026)
- Kibana : http://localhost:5601
- Backend API : http://localhost:8000/health
- Documentation Swagger : http://localhost:8000/docs

### Arrêter les services
docker compose down

---

## 5. Structure du dépôt Git
smart-siem/

├── .github/

│   └── workflows/

│       └── ci.yml          # Pipeline CI/CD GitHub Actions

├── backend/

│   ├── app/

│   │   ├── api/v1/         # Endpoints FastAPI

│   │   ├── core/           # Moteur de corrélation (à venir)

│   │   ├── database/       # Connexion Elasticsearch (à venir)

│   │   └── schemas/        # Modèles Pydantic

│   ├── Dockerfile

│   └── requirements.txt

├── frontend/

│   └── Dockerfile

├── filebeat/

│   └── filebeat.yml        # Config agent de collecte

├── scripts/

│   └── rollback.sh         # Script de rollback

├── docs/

│   └── ci-cd.md            # Documentation pipeline

├── logs/                   # Logs locaux (ignoré par Git)

├── .env                    # Secrets locaux (ignoré par Git)

├── .flake8                 # Config lint Python

├── .gitignore

├── docker-compose.yml

└── README.md

### Stratégie de branches
| Branche | Rôle |
|---|---|
| main | Production, protégée, merge par PR uniquement |
| develop | Intégration, branche de travail principale |
| feature/* | Une branche par fonctionnalité/membre |

---

## 6. Gestion des secrets

Aucun secret n'est commité dans le dépôt Git. Tous les secrets sont gérés
via deux mécanismes :

**En local :** fichier `.env` à la racine (présent dans `.gitignore`)

**En CI/CD :** GitHub Actions Secrets

| Nom du secret | Utilité                                       |
|-----------|-----------------------------------------------|
|  ELASTIC_PASSWORD         | Mot de passe Elasticsearch |
| ELASTIC_USERNAME   | Utilisateur Elasticsearch    |
| KIBANA_TOKEN | Token de service Kibana         |
| GHCR_TOKEN | Token GitHub Container Registry         |

---

## 7. À compléter ultérieurement

- Procédure de déploiement sur l'environnement de production (en attente Infra)
- Configuration TLS en production
- Procédure de restauration des données Elasticsearch