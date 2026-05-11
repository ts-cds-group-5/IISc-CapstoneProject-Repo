"""Authentication models for CCCP Advanced API."""

from typing import Literal
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request model for login endpoint."""

    username: str = Field(..., description="Admin username or email")
    password: str = Field(..., description="Admin password")


class TokenResponse(BaseModel):
    """Response model for token generation."""

    access_token: str = Field(..., description="JWT access token")
    token_type: Literal["bearer"] = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token validity in seconds")


class CurrentUser(BaseModel):
    """Current authenticated user context."""

    username: str = Field(..., description="Authenticated username")
    email: str = Field(..., description="Authenticated email")
