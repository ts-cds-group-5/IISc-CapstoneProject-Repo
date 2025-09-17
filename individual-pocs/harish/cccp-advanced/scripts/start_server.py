#!/usr/bin/env python3
"""Start the FastAPI server for CCCP Advanced."""

import sys
import uvicorn
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from cccp.core.config import get_settings
from cccp.core.logging import setup_logging, get_logger

def main():
    """Main entry point for starting the server."""
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Get settings
    settings = get_settings()
    
    logger.info(f"Starting CCCP Advanced server v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Start server
    uvicorn.run(
        "cccp.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main()

