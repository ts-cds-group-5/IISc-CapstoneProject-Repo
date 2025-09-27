"""Health check routes for CCCP Advanced API."""

import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from cccp.core.logging import get_logger
from cccp.core.config import get_settings
from cccp.api.models.responses import HealthResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])

# Track start time for uptime calculation
_start_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint."""
    try:
        settings = get_settings()
        uptime = time.time() - _start_time
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            uptime=uptime,
            components={
                "api": "running",
                "logging": "active"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.get("/ready", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """Readiness check endpoint (includes model loading)."""
    try:
        settings = get_settings()
        uptime = time.time() - _start_time
        
        # Check if model is loaded (this will be implemented later)
        components = {
            "api": "running",
            "logging": "active",
            "model": "not_checked"  # Will be updated when model service is ready
        }
        
        return HealthResponse(
            status="ready",
            version=settings.app_version,
            uptime=uptime,
            components=components
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live", response_model=HealthResponse)
async def liveness_check() -> HealthResponse:
    """Liveness check endpoint (basic service check)."""
    try:
        settings = get_settings()
        uptime = time.time() - _start_time
        
        return HealthResponse(
            status="alive",
            version=settings.app_version,
            uptime=uptime,
            components={"api": "running"}
        )
    except Exception as e:
        logger.error(f"Liveness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not alive")

