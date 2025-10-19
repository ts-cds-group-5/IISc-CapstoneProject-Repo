"""
MCP (Model Context Protocol) module for CCCP.

This module provides PostgreSQL integration through MCP protocol,
including database client and configuration management.
"""

from .client import MCPPostgresClient

__all__ = [
    "MCPPostgresClient",
]

__version__ = "1.0.0"
