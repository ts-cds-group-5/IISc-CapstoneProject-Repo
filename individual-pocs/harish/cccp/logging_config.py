"""
Logging configuration for the CCCP project.
This module provides a centralized logging setup that can be imported by all modules.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logging(level=logging.INFO, log_to_file=False):
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level (default: INFO)
        log_to_file: Whether to also log to a file (default: False)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_to_file:
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"cccp_{timestamp}.log"
        handlers.append(logging.FileHandler(log_file))
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Set specific loggers
    loggers = [
        "server_api",
        "mspb_model", 
        "streamlit_ui",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi"
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    # Reduce noise from some libraries
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logging.getLogger("cccp")

def get_logger(name: str):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the module (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

# Initialize default logging
logger = setup_logging()
