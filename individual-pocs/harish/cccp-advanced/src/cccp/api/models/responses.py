"""Response models for CCCP Advanced API."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Response model for chat endpoints."""
    
    response: str = Field(..., description="The generated response")
    status: str = Field(default="success", description="Response status")
    user_id: str = Field(..., description="User identifier")
    tool_used: Optional[str] = Field(default=None, description="Tool that was used")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "The result of 5 + 3 is 8",
                "status": "success",
                "user_id": "user123",
                "tool_used": "multiply",
                "metadata": {"generation_time": 0.5}
            }
        }


class ToolResponse(BaseModel):
    """Response model for tool endpoints."""
    
    result: Any = Field(..., description="Tool execution result")
    status: str = Field(..., description="Execution status")
    tool_name: str = Field(..., description="Name of the executed tool")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "result": 15,
                "status": "success",
                "tool_name": "multiply",
                "execution_time": 0.1
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error cases."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    status: str = Field(default="error", description="Response status")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Model not loaded",
                "error_code": "MODEL_ERROR",
                "status": "error",
                "details": {"model_name": "microsoft/phi-2"}
            }
        }


class MCPResponse(BaseModel):
    """Response model for MCP server endpoints."""
    
    result: Any = Field(..., description="MCP method result")
    request_id: Optional[str] = Field(default=None, description="Request identifier")
    status: str = Field(default="success", description="Response status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "result": {"tools": ["multiply", "add", "subtract"]},
                "request_id": "req123",
                "status": "success"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoints."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    uptime: Optional[float] = Field(default=None, description="Service uptime in seconds")
    components: Optional[Dict[str, str]] = Field(default=None, description="Component statuses")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "uptime": 3600.5,
                "components": {
                    "model": "loaded",
                    "mcp_server": "running",
                    "database": "connected"
                }
            }
        }

