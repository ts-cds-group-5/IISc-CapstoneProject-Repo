"""Authentication routes for CCCP Advanced API."""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from cccp.api.auth import create_access_token, verify_admin_credentials
from cccp.api.models.auth import LoginRequest, TokenResponse
from cccp.core.config import get_settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """Authenticate admin user and issue JWT token."""
    if not verify_admin_credentials(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )

    settings = get_settings()
    expires_in = settings.auth_access_token_expire_minutes * 60
    token = create_access_token(
        {
            "username": settings.auth_admin_username,
            "email": settings.auth_admin_email,
        },
        expires_delta=timedelta(minutes=settings.auth_access_token_expire_minutes),
    )

    return TokenResponse(access_token=token, expires_in=expires_in)
