#!/usr/bin/env python3
"""Main entry point for CCCP Advanced."""

import sys
import argparse
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from cccp.core.logging import setup_logging, get_logger
from cccp.core.config import get_settings


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CCCP Advanced - Conversational Chatbot")
    parser.add_argument(
        "command",
        choices=["server", "ui", "test"],
        help="Command to run"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (for server)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (for server)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Get settings
    settings = get_settings()
    
    if args.command == "server":
        logger.info("Starting CCCP Advanced server...")
        import uvicorn
        uvicorn.run(
            "cccp.api.server:app",
            host=args.host,
            port=args.port,
            reload=args.debug,
            log_level="debug" if args.debug else "info"
        )
    
    elif args.command == "ui":
        logger.info("Starting CCCP Advanced UI...")
        import subprocess
        streamlit_app = project_root / "src" / "cccp" / "ui" / "streamlit_app.py"
        subprocess.run([
            "streamlit", "run", str(streamlit_app),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    
    elif args.command == "test":
        logger.info("Running tests...")
        import subprocess
        subprocess.run(["pytest", "tests/", "-v"])


if __name__ == "__main__":
    main()

