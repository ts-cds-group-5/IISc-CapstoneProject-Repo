"""API package for CCCP Advanced."""

def create_app():
    """Create FastAPI app lazily to avoid import side effects."""
    from cccp.api.server import create_app as _create_app
    return _create_app()

__all__ = ["create_app"]

