"""Authentication helpers for JWT login and route protection."""

from datetime import datetime, timedelta, timezone
import hmac
from typing import Any, Dict

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from cccp.api.models.auth import CurrentUser
from cccp.core.config import get_settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _unauthorized_exception(detail: str = "Could not validate credentials") -> HTTPException:
    """Build a consistent 401 response."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_admin_credentials(username: str, password: str) -> bool:
    """Validate login credentials against env-seeded admin user."""
    settings = get_settings()
    username_matches = hmac.compare_digest(username, settings.auth_admin_username) or hmac.compare_digest(
        username, settings.auth_admin_email
    )
    password_matches = hmac.compare_digest(password, settings.auth_admin_password)
    return username_matches and password_matches


def create_access_token(subject: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token."""
    settings = get_settings()
    expiry = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.auth_access_token_expire_minutes)
    )
    payload = {
        **subject,
        "exp": expiry,
        "iat": datetime.now(timezone.utc),
        "sub": subject.get("username"),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.auth_jwt_algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT access token."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.auth_jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise _unauthorized_exception() from exc
    return payload


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """Resolve current user from bearer token."""
    payload = decode_access_token(token)
    username = payload.get("username")
    email = payload.get("email")

    if not username or not email:
        raise _unauthorized_exception("Token payload missing required claims")

    settings = get_settings()
    if not (
        hmac.compare_digest(username, settings.auth_admin_username)
        and hmac.compare_digest(email, settings.auth_admin_email)
    ):
        raise _unauthorized_exception()

    return CurrentUser(username=username, email=email)
