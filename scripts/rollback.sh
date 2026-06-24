#!/bin/bash
# rollback.sh — Revenir à une version précédente des images Docker
# Usage : ./scripts/rollback.sh <SHA_DU_COMMIT>
# Exemple : ./scripts/rollback.sh a1b2c3d4e5f6...

set -e

OWNER=$(echo "$GITHUB_REPOSITORY_OWNER" | tr '[:upper:]' '[:lower:]')
SHA=$1

if [ -z "$SHA" ]; then
  echo "❌ Erreur : tu dois fournir le SHA du commit."
  echo "Usage : ./scripts/rollback.sh <SHA_DU_COMMIT>"
  echo "Les SHA disponibles sont visibles dans l'onglet Packages de GitHub."
  exit 1
fi

echo "🔄 Rollback vers la version : $SHA"

# Mettre à jour les images dans le compose vers la version demandée
BACKEND_IMAGE="ghcr.io/$OWNER/smart-siem-backend:$SHA"
FRONTEND_IMAGE="ghcr.io/$OWNER/smart-siem-frontend:$SHA"

echo "📦 Backend  : $BACKEND_IMAGE"
echo "📦 Frontend : $FRONTEND_IMAGE"

# Redémarrer les services avec les anciennes images
docker pull "$BACKEND_IMAGE"
docker pull "$FRONTEND_IMAGE"

BACKEND_IMAGE=$BACKEND_IMAGE FRONTEND_IMAGE=$FRONTEND_IMAGE docker compose up -d backend frontend

echo "✅ Rollback terminé avec succès."