"""
Module central de sécurité du Smart SIEM.

Remplace l'authentification factice précédente (username == "admin" and
password == "admin", token en dur "FAKE_JWT_TOKEN_FOR_DEMO_SECRET") par :
  - un hash de mot de passe réel (bcrypt, via passlib) ;
  - un JWT réellement signé (HS256, expiration, vérification de signature) ;
  - un second facteur TOTP (RFC 6238, via pyotp), conforme à l'exigence du
    cahier des charges section 4.7.

⚠️ SECRET_KEY : en dur ici uniquement pour que le projet démarre "out of the
box" en environnement étudiant. Avant toute démonstration réelle, sortez-la
dans une variable d'environnement (`os.getenv("SIEM_SECRET_KEY")`) et ne la
committez jamais dans le dépôt Git.
"""

import os
import pyotp
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SIEM_SECRET_KEY", "ctu-smart-siem-dev-secret-CHANGE-ME-EN-PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Jeton "intermédiaire" émis après vérification du mot de passe mais avant le TOTP.
# Sa durée de vie est volontairement très courte : il ne permet RIEN d'autre
# que de présenter le code MFA.
MFA_PENDING_TOKEN_EXPIRE_MINUTES = 5

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─────────────────────────────────────────────────────────────────────────
# 1. MOTS DE PASSE
# ─────────────────────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────
# 2. JWT
# ─────────────────────────────────────────────────────────────────────────

def create_access_token(subject: str, role: str, extra: Optional[Dict] = None) -> str:
    """Crée un JWT signé, seul jeton accepté par le SIEM une fois le MFA validé."""
    to_encode = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    if extra:
        to_encode.update(extra)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_mfa_pending_token(subject: str) -> str:
    """Jeton temporaire émis juste après validation du mot de passe, avant le TOTP."""
    to_encode = {
        "sub": subject,
        "type": "mfa_pending",
        "exp": datetime.utcnow() + timedelta(minutes=MFA_PENDING_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict]:
    """Décode et VÉRIFIE la signature + l'expiration. Renvoie None si invalide."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ─────────────────────────────────────────────────────────────────────────
# 3. MFA / TOTP (RFC 6238)
# ─────────────────────────────────────────────────────────────────────────

def generate_totp_secret() -> str:
    """Génère un secret TOTP unique pour un utilisateur (à stocker chiffré côté serveur)."""
    return pyotp.random_base32()


def get_totp_provisioning_uri(secret: str, username: str, issuer: str = "Smart SIEM CTU") -> str:
    """URI otpauth:// à encoder en QR code pour l'app d'authentification (Google Authenticator, etc.)."""
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)


def verify_totp_code(secret: str, code: str) -> bool:
    """Vérifie un code TOTP à 6 chiffres, avec une tolérance de +/-1 fenêtre de 30s
    pour absorber un léger décalage d'horloge entre client et serveur."""
    if not secret or not code:
        return False
    totp = pyotp.totp.TOTP(secret)
    return totp.verify(code, valid_window=1)
