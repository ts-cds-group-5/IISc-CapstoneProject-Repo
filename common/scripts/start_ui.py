#!/usr/bin/env python3
"""Start the Streamlit UI for CCCP Advanced."""

import sys
import subprocess
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from cccp.core.config import get_settings
from cccp.core.logging import setup_logging, get_logger

def main():
    """Main entry point for starting the UI."""
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Get settings
    settings = get_settings()
    
    logger.info(f"Starting CCCP Advanced UI v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Get the streamlit app path
    streamlit_app_path = project_root / "src" / "cccp" / "ui" / "streamlit_app.py"
    
    # Start Streamlit
    try:
        subprocess.run([
            "streamlit", "run", str(streamlit_app_path),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Streamlit: {e}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error("Streamlit not found. Please install it with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()

