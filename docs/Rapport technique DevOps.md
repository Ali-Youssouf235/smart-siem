# Rapport Technique — Ingénieur DevOps
# Smart SIEM — Projet étudiant transversal

Auteur : ALI YOUSSOUF
Rôle : Ingénieur DevOps
Date : 27/06/2026

---

## 1. Résumé exécutif

Dans le cadre du projet Smart SIEM, j'ai mis en place l'ensemble de
l'infrastructure CI/CD permettant d'automatiser le cycle de vie du code
de toute l'équipe. Le pipeline GitHub Actions couvre aujourd'hui le lint,
le build Docker, le scan de sécurité, les notifications d'échec et la
structure du déploiement continu. Tous les services du projet sont
conteneurisés et orchestrés via Docker Compose.

---

## 2. Gouvernance Git

### Stratégie de branches
- `main` : branche de production, protégée, merge uniquement via Pull
  Request avec review obligatoire
- `develop` : branche d'intégration, point de convergence de tous les
  membres de l'équipe
- `feature/*` : une branche par membre/fonctionnalité

### Conventions de commits
Format : `type: description courte`
Types utilisés : `feat`, `fix`, `ci`, `docs`, `docker`, `security`,
`devops`, `merge`

### Résultats
- 0 commit direct sur `main`
- Toutes les branches des membres intégrées dans `develop` via merge
  contrôlé
- Aucun conflit Git non résolu

---

## 3. Pipeline CI/CD

### Outil
GitHub Actions — fichier `.github/workflows/ci.yml`

### Jobs implémentés

#### Job 1 : lint
- Outil : flake8
- Configuration : fichier `.flake8` à la racine
- Résultat : pipeline bloqué si erreur critique détectée

#### Job 2 : build-and-push
- Build des images Docker backend et frontend
- Push vers GitHub Container Registry
- Double tagging : `latest` + SHA du commit (pour traçabilité et rollback)
- Correction de la contrainte lowercase GHCR via `tr '[:upper:]' '[:lower:]'`

#### Job 3 : security-scan
- Outil : Trivy
- Cible : image backend
- Sévérités remontées : CRITICAL et HIGH
- Mode non-bloquant (exit-code: 0) pour ne pas bloquer le développement

#### Job 4 : notify-failure
- Déclenché uniquement en cas d'échec d'un job précédent
- Affiche : branche, SHA, auteur, lien vers les logs

#### Job 5 : deploy
- Structure en place, connexion à l'environnement cible en cours
  (en attente Ingénieur Infra)

---

## 4. Conteneurisation

### Services Docker Compose
| Service | Image | Port |
|---|---|---|
| backend | Build local FastAPI | 8000 |
| frontend | Build local Node | 3000 |
| elasticsearch | 8.13.0 | 9200 |
| kibana | 8.13.0 | 5601 |
| filebeat | 8.13.0 | — |

### Fonctionnalités
- Réseau interne `siem-network` isolé
- Volume persistant `elasticsearch-data`
- Healthcheck Elasticsearch avant démarrage de Filebeat et Kibana
- Redémarrage automatique (`restart: unless-stopped`)

---

## 5. Gestion des secrets

### Principe appliqué
Aucun secret n'est commité dans le dépôt Git. Règle vérifiée sur
l'ensemble de l'historique.

### Mécanisme
- **Local** : fichier `.env` à la racine, présent dans `.gitignore`
- **Pipeline** : GitHub Actions Secrets

### Secrets gérés
| Secret | Utilité |
|---|---|
| ELASTIC_PASSWORD | Authentification Elasticsearch |
| ELASTIC_USERNAME | Authentification Elasticsearch |
| KIBANA_TOKEN | Token service Kibana |
| GHCR_TOKEN | Authentification registre d'images |

### Incidents signalés
- Credentials en dur dans les fichiers Python de l'Ingénieur Data
  (signalé le 24/06/2026, correction en attente)

---

## 6. Registre d'images

- **Plateforme** : GitHub Container Registry (GHCR)
- **Images publiées** :
    - `ghcr.io/<owner>/smart-siem-backend`
    - `ghcr.io/<owner>/smart-siem-frontend`
- **Visibilité** : publique
- **Tags** : `latest` + SHA du commit à chaque build

---

## 7. Rollback

### Script
`scripts/rollback.sh <SHA_DU_COMMIT>`

### Fonctionnement
1. Récupère l'image correspondant au SHA demandé depuis GHCR
2. Redémarre les services backend et frontend avec cette image
3. Confirme le succès du rollback

---

## 8. Serveur central Elasticsearch

Suite à la décision d'équipe du 27/06/2026, la machine DevOps héberge
l'instance Elasticsearch centrale partagée par toute l'équipe. Ports
9200 et 5601 ouverts dans le pare-feu Windows.

---

## 9. Points en attente

| Point | Bloquant | Responsable |
|---|---|---|
| Connexion job CD à l'environnement cible | Oui | Ingénieur Infra |
| Correction credentials en dur Data | Non | Ingénieur Data |
| Intégration code Frontend dans pipeline | Non | Dev Frontend |
| Tests unitaires dans CI | Non | Dev Backend |