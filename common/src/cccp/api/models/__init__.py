"""API models for CCCP Advanced."""

from cccp.api.models.requests import ChatRequest, ToolRequest
from cccp.api.models.responses import ChatResponse, ToolResponse, ErrorResponse

__all__ = [
    "ChatRequest",
    "ToolRequest", 
    "ChatResponse",
    "ToolResponse",
    "ErrorResponse",
]

