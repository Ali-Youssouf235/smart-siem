"""
Dépendances FastAPI pour l'authentification et le RBAC.

⚠️ Avant ce fichier, `dependencies.py` était VIDE : aucune route ne vérifiait
jamais de token. N'importe quel client pouvait appeler n'importe quel
endpoint (y compris administration des utilisateurs, suppression de règles,
changement de politique de rétention) sans être authentifié.

`get_current_user` doit désormais être injecté via `Depends(...)` sur toute
route qui ne doit pas être publique.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict

from app.core.security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)

# Hiérarchie des rôles : un rôle "supérieur" hérite implicitement des droits
# des rôles inférieurs pour les dépendances `require_role`.
ROLE_HIERARCHY = {"lecteur": 0, "analyste": 1, "admin": 2}


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict:
    """
    Vérifie la présence et la validité (signature + expiration) du JWT.
    Lève une 401 si absent/invalide/expiré, ou si ce n'est pas un jeton
    d'accès final (ex: un jeton MFA intermédiaire non finalisé).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise (token JWT manquant).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide, expiré, ou authentification MFA non finalisée.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "username": payload.get("sub"),
        "role": payload.get("role", "lecteur"),
        "perimetre_id": payload.get("perimetre_id"),
    }


def require_role(minimum_role: str):
    """
    Fabrique une dépendance FastAPI qui exige un rôle minimum (selon
    ROLE_HIERARCHY). Ex: Depends(require_role("admin")) sur les routes
    d'administration des utilisateurs ou de suppression de règles.
    """
    async def _dependency(current_user: Dict = Depends(get_current_user)) -> Dict:
        user_level = ROLE_HIERARCHY.get(current_user["role"], -1)
        required_level = ROLE_HIERARCHY.get(minimum_role, 99)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Privilège insuffisant : rôle '{minimum_role}' minimum requis.",
            )
        return current_user

    return _dependency
