"""API routes for CCCP Advanced."""

from cccp.api.routes.chat import router as chat_router
from cccp.api.routes.tools import router as tools_router
from cccp.api.routes.health import router as health_router

__all__ = [
    "chat_router",
    "tools_router", 
    "health_router",
]

