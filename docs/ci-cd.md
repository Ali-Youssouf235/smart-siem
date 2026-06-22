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