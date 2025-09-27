"""Logging configuration for CCCP Advanced."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from cccp.core.config import get_settings, get_logs_dir


def setup_logging(
    level: Optional[str] = None,
    log_to_file: Optional[bool] = None,
    log_file_path: Optional[str] = None,
) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level (default: from settings)
        log_to_file: Whether to also log to a file (default: from settings)
        log_file_path: Path to log file (default: from settings)
    """
    settings = get_settings()
    
    # Use provided values or fall back to settings
    log_level = level or settings.log_level
    log_to_file = log_to_file if log_to_file is not None else settings.log_to_file
    log_file_path = log_file_path or settings.log_file_path
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory if needed
    if log_to_file:
        logs_dir = get_logs_dir()
        if not log_file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file_path = logs_dir / f"cccp_{timestamp}.log"
        else:
            log_file_path = Path(log_file_path)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_to_file:
        handlers.append(logging.FileHandler(log_file_path))
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
        force=True,  # Override any existing configuration
    )
    
    # Set specific loggers
    loggers = [
        "cccp",
        "cccp.api",
        "cccp.agents",
        "cccp.tools",
        "cccp.mcp",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)
    
    # Reduce noise from some libraries
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Log the setup
    logger = logging.getLogger("cccp.core.logging")
    logger.info(f"Logging configured - Level: {log_level}, File: {log_to_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the module (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")

