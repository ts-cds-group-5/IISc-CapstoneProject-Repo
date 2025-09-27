"""Request models for CCCP Advanced API."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoints."""
    
    prompt: str = Field(..., description="The user's prompt or message")
    user_id: str = Field(default="default_user", description="User identifier")
    max_length: Optional[int] = Field(default=None, description="Maximum response length")
    temperature: Optional[float] = Field(default=None, description="Sampling temperature")
    use_tools: bool = Field(default=True, description="Whether to use available tools")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What is 5 + 3?",
                "user_id": "user123",
                "max_length": 256,
                "temperature": 0.2,
                "use_tools": True
            }
        }


class ToolRequest(BaseModel):
    """Request model for tool endpoints."""
    
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    user_id: str = Field(default="default_user", description="User identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "multiply",
                "parameters": {"a": 5, "b": 3},
                "user_id": "user123"
            }
        }


class MCPRequest(BaseModel):
    """Request model for MCP server endpoints."""
    
    method: str = Field(..., description="MCP method to call")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Method parameters")
    request_id: Optional[str] = Field(default=None, description="Request identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "method": "tools/list",
                "params": {},
                "request_id": "req123"
            }
        }

