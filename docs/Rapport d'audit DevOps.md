# Rapport d'audit sécurité final — Volet DevOps
# Smart SIEM

Auteur : ALI YOUSSOUF
Rôle : Ingénieur DevOps
Date : 27/06/2026
Statut : En cours (sections finales à compléter en Semaine 3)

---

## 1. Périmètre audité

- Pipeline CI/CD (GitHub Actions)
- Images Docker (backend, frontend)
- Fichiers de configuration committés (docker-compose.yml, filebeat.yml,
  ci.yml, .flake8)
- Gestion des secrets
- Stratégie de branches et accès au dépôt

---

## 2. Audit des secrets

### Règle
Zéro secret en clair dans le dépôt Git.

### Résultat
| Fichier | Secret présent en clair | Statut |
|---|---|---|
| docker-compose.yml | Non (variables ${}) | ✅ Conforme |
| filebeat/filebeat.yml | Non (variables ${}) | ✅ Conforme |
| .github/workflows/ci.yml | Non (secrets GitHub) | ✅ Conforme |
| backend/Dockerfile | Non | ✅ Conforme |
| frontend/Dockerfile | Non | ✅ Conforme |

### Non-conformités identifiées chez d'autres membres
- `pipeline.py` (Data) : `siem2026` en clair — signalé le 24/06
- `setup_indices.py` (Data) : `siem2026` en clair — signalé le 24/06
- `retention_policy.py` (Data) : `siem2026` en clair — signalé le 24/06
- `export.py` (Data) : `siem2026` en clair — à signaler
- `rbac.py` (Data) : `siem2026` en clair — à signaler
- `report_generator.py` (Data) : `siem2026` en clair — à signaler
- `search.py` (Data) : `siem2026` en clair — à signaler

---

## 3. Audit du pipeline CI/CD

| Contrôle | Résultat |
|---|---|
| Lint automatique actif | ✅ |
| Build échoue si lint échoue | ✅ |
| Images scannées par Trivy | ✅ |
| Secrets injectés via GitHub Secrets | ✅ |
| GITHUB_TOKEN avec permissions minimales | ✅ |
| Branche main protégée | ✅ |
| Notification d'échec active | ✅ |
| Double tagging pour traçabilité | ✅ |

---

## 4. Audit des images Docker

### Outil
Trivy — intégré dans le pipeline (job `security-scan`)

### Résultats des scans
À compléter ultérieurement après analyse complète des rapports Trivy
en fin de projet.

---

## 5. Audit de la stratégie Git

| Contrôle | Résultat |
|---|---|
| Branche main protégée (PR obligatoire) | ✅ |
| Convention de commits respectée | ✅ |
| Fichiers sensibles dans .gitignore | ✅ |
| Aucun secret dans l'historique Git | ✅ |
| Branches de travail séparées par membre | ✅ |

---

## 6. Conformité RGPD / ISO 27001

À compléter ultérieurement en Semaine 3.



---

## 7. Recommandations

| Priorité | Recommandation | Responsable |
|---|---|---|
| Haute | Corriger tous les credentials en dur dans le code Data | Ingénieur Data |
| Haute | Activer TLS sur toutes les communications en production | Infra + DevOps |
| Moyenne | Ajouter des tests unitaires dans le pipeline CI | Dev Backend |
| Moyenne | Limiter les privilèges des conteneurs (non-root) | DevOps |
| Basse | Mettre en place un monitoring des pipelines (Grafana) | DevOps |