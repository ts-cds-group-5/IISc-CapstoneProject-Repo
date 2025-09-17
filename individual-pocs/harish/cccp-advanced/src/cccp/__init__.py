"""
CCCP Advanced - Conversational Chatbot with LangGraph and MCP Server

A modern, scalable conversational AI system built with FastAPI, LangGraph,
and MCP (Model Context Protocol) server capabilities.
"""

__version__ = "0.1.0"
__author__ = "Harish"
__email__ = "harish@example.com"

from cccp.core.config import get_settings
from cccp.core.logging import setup_logging

# Initialize logging when package is imported
setup_logging()

# Export main components
__all__ = [
    "get_settings",
    "setup_logging",
    "__version__",
    "__author__",
    "__email__",
]

