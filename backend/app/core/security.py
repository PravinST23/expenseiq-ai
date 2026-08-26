"""
Security - Password Hashing & JWT Access Tokens

Author: Pravin Shanmugavel
Project: ExpenseIQ

Uses `bcrypt` directly (not passlib) - passlib 1.7.x cannot detect
modern bcrypt (>=4.x) backends and raises on import/hash in this
environment. `python-jose` handles JWT encode/decode.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.config.settings import settings

# bcrypt silently truncates/errors past 72 bytes - cap defensively
# rather than let a long password produce a confusing 500.
_MAX_PASSWORD_BYTES = 72

TOKEN_TYPE = "bearer"


class InvalidTokenError(Exception):
    """Raised when a JWT is missing, malformed, expired, or forged."""


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password for storage.
    """

    password_bytes = plain_password.encode("utf-8")[:_MAX_PASSWORD_BYTES]

    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.
    """

    password_bytes = plain_password.encode("utf-8")[:_MAX_PASSWORD_BYTES]

    try:
        return bcrypt.checkpw(
            password_bytes,
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        # Malformed/legacy hash (e.g. no password ever set)
        return False


def create_access_token(
    *,
    employee_id: UUID,
    role: str,
    expires_minutes: int | None = None,
) -> tuple[str, datetime]:
    """
    Issue a signed JWT access token for an authenticated employee.

    Returns (token, expires_at) so the caller can surface the
    expiry to the client without re-decoding the token.
    """

    if expires_minutes is None:
        expires_minutes = settings.JWT_EXPIRE_MINUTES

    expires_delta = timedelta(minutes=expires_minutes)

    expires_at = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(employee_id),
        "role": role,
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token, expires_at


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Raises InvalidTokenError on any failure - missing/invalid
    signature, malformed payload, or an expired `exp` claim
    (python-jose enforces expiration automatically).
    """

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as ex:
        raise InvalidTokenError(str(ex)) from ex

    subject = payload.get("sub")

    if subject is None:
        raise InvalidTokenError("Token is missing a subject claim.")

    return payload
