# Pipeline CI/CD — Smart SIEM

## Objectif
Ce document décrit le fonctionnement du pipeline d'intégration et de déploiement continu du projet Smart SIEM.

## Statut
Workflow CI placeholder fonctionnel (Jour 3). Se déclenche sur push et pull request.

## Déclencheurs
- Push sur `main`, `develop`, ou toute branche `feature/**`
- Pull request vers `main` ou `develop`

## Étapes actuelles du pipeline
1. Checkout du code
2. Vérification que le pipeline se déclenche correctement (placeholder)

## Prochaines étapes prévues
- Ajout du lint
- Ajout des tests unitaires (dépend du code fourni par le Dev Backend/Frontend)
- Build des images Docker
- Scan de sécurité (Trivy)
- Push vers le registre d'images
- Déploiement automatisé (CD)

## Structure
- `.github/workflows/` : workflows GitHub Actions
- `backend/` : code source backend
- `frontend/` : code source frontend

## Conteneurisation
- `backend/Dockerfile` : image Python placeholder (port 8000), à remplacer par le vrai build une fois le code backend disponible
- `frontend/Dockerfile` : image Node placeholder (port 3000), à remplacer par le vrai build une fois le code frontend disponible
- `docker-compose.yml` : orchestration locale backend + frontend, testée avec succès le 22/06
- Base de données : pas encore intégrée au compose, en attente de la décision technique de l'Ingénieur Data

## Livrable Semaine 1 — État au 23/06/2026
- Pipeline CI fonctionnel : déclenchement sur push/PR, vérifié.
- Images Docker (placeholder) buildées et publiées automatiquement sur GitHub Container Registry à chaque push.
- Docker Compose local fonctionnel (backend + frontend, testé le 22/06).
- En attente : code réel du backend et du frontend pour remplacer les placeholders.
- Prochaine étape : intégration du lint et des tests dès que le code applicatif est disponible.

## Jour 6 — Pipeline CI complet (24/06/2026)

### Jobs actifs
1. **lint** : vérification du code Python backend avec flake8
    - Config dans `.flake8` à la racine du projet
    - Déclenché sur tout push/PR
2. **build-and-push** : build et push des images Docker vers GHCR
    - Se lance uniquement si le lint est passé
    - Conversion du nom du owner en minuscules via bash (exigence GHCR)
3. **security-scan** : scan des vulnérabilités avec Trivy
    - Se lance uniquement si le build est passé
    - Remonte les vulnérabilités CRITICAL et HIGH

### Ordre d'exécution
lint → build-and-push → security-scan

### Point en attente
- Le Dev Backend doit supprimer l'import inutilisé `typing.Dict` dans `app/core/engine.py`

## Jour 7 — Versioning et rollback (25/06/2026)

### Tags d'images
Chaque build pousse deux tags vers GHCR :
- `latest` : toujours la version la plus récente
- `<SHA_du_commit>` : version exacte liée au commit Git

### Procédure de rollback
En cas de problème sur la version déployée :
1. Trouver le SHA du commit stable dans l'onglet Packages de GitHub
2. Exécuter : `./scripts/rollback.sh <SHA_DU_COMMIT>`
3. Le script redémarre automatiquement backend et frontend avec l'ancienne image

### Packages GHCR
- `smart-siem-backend` : image Python/FastAPI
- `smart-siem-frontend` : image Node placeholder (en attente du code frontend)

## Jour 8 — Notifications et audit secrets (26/06/2026)

### Notifications d'échec
- Email automatique GitHub activé pour tout échec de workflow
- Job `notify-failure` dans le pipeline : s'exécute uniquement en cas
  d'échec, affiche le résumé (branche, commit, auteur, lien direct)

### Audit des secrets — état au 26/06/2026
| Secret | Stockage | Statut |
|---|---|---|
| ELASTIC_PASSWORD | .env + GitHub Actions Secrets | ✅ Sécurisé |
| ELASTIC_USERNAME | .env + GitHub Actions Secrets | ✅ Sécurisé |
| KIBANA_TOKEN | .env + GitHub Actions Secrets | ✅ Sécurisé |
| GHCR_TOKEN | GitHub Actions Secrets | ✅ Sécurisé |

### Règle absolue
Aucun secret ne doit être commité dans le repo.
Tout secret doit être dans `.env` (local, ignoré par Git)
et dans GitHub Actions Secrets (pipeline).

## Jour 9 — Test intégration complète et structure CD (27/06/2026)

### Test docker compose complet
Tous les services testés ensemble :
- Elasticsearch : ✅
- Kibana : ✅
- Filebeat : ✅
- Backend FastAPI : ✅
- Frontend : placeholder (en attente du code Dev Frontend)

### Job CD ajouté
- Se déclenche uniquement sur la branche `main`
- En attente de l'environnement cible préparé par l'Ingénieur Infra
- Sera connecté au Jour 10

### Blocages identifiés
- Frontend : pas encore de code disponible
- Ingénieur Data : credentials en dur dans le code Python (signalé)

## Serveur Elasticsearch central — décision d'équipe (27/06/2026)

### Contexte
Chaque membre lançait sa propre instance Elasticsearch locale, créant des
bases de données différentes et désynchronisées (Data et Backend
travaillaient sur deux instances séparées).

### Décision
La machine du DevOps (Ali) sert de serveur central Elasticsearch/Kibana
pour toute l'équipe, le temps que l'Infra finalise l'environnement de
déploiement définitif.

### Configuration
- Port 9200 (Elasticsearch) et 5601 (Kibana) ouverts dans le pare-feu Windows
- URL communiquée à l'équipe : http://[IP_LOCALE]:9200
- Cette IP changera lors du passage sur l'environnement Infra définitif (Jour 10)