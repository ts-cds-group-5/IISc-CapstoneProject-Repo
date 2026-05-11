"""Unit tests for API authentication."""

from datetime import timedelta

from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient

from cccp.api.auth import create_access_token, get_current_user
from cccp.api.routes.auth import router as auth_router
from cccp.core.config import get_settings


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router, prefix="/api/v1")

    protected_router = APIRouter(prefix="/api/v1/protected", dependencies=[Depends(get_current_user)])

    @protected_router.get("/ping")
    async def protected_ping() -> dict:
        return {"status": "ok"}

    app.include_router(protected_router)
    return app


def test_login_success(monkeypatch):
    monkeypatch.setenv("AUTH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("AUTH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("AUTH_ADMIN_PASSWORD", "super-secret")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    get_settings.cache_clear()

    client = TestClient(_build_test_app())
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "super-secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["expires_in"] > 0

    get_settings.cache_clear()


def test_login_failure(monkeypatch):
    monkeypatch.setenv("AUTH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("AUTH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("AUTH_ADMIN_PASSWORD", "super-secret")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    get_settings.cache_clear()

    client = TestClient(_build_test_app())
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )

    assert response.status_code == 401

    get_settings.cache_clear()


def test_protected_endpoint_requires_token():
    client = TestClient(_build_test_app())
    response = client.get("/api/v1/protected/ping")
    assert response.status_code == 401


def test_protected_endpoint_with_valid_token(monkeypatch):
    monkeypatch.setenv("AUTH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("AUTH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("AUTH_ADMIN_PASSWORD", "super-secret")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    get_settings.cache_clear()

    token = create_access_token({"username": "admin", "email": "admin@example.com"})
    client = TestClient(_build_test_app())
    response = client.get("/api/v1/protected/ping", headers=_auth_headers(token))

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    get_settings.cache_clear()


def test_protected_endpoint_with_expired_token(monkeypatch):
    monkeypatch.setenv("AUTH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("AUTH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("AUTH_ADMIN_PASSWORD", "super-secret")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    get_settings.cache_clear()

    expired_token = create_access_token(
        {"username": "admin", "email": "admin@example.com"},
        expires_delta=timedelta(seconds=-1),
    )
    client = TestClient(_build_test_app())
    response = client.get("/api/v1/protected/ping", headers=_auth_headers(expired_token))

    assert response.status_code == 401

    get_settings.cache_clear()
