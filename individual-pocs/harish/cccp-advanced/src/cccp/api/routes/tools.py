"""Tool routes for CCCP Advanced API."""

import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from cccp.core.logging import get_logger
from cccp.core.exceptions import ToolError
from cccp.api.models.requests import ToolRequest
from cccp.api.models.responses import ToolResponse, ErrorResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/tools", tags=["tools"])


# Tool implementations
def multiply_tool(a: int, b: int) -> int:
    """Multiply two numbers."""
    logger.debug(f"Executing multiply tool: {a} * {b}")
    try:
        result = a * b
        logger.info(f"Multiply result: {a} * {b} = {result}")
        return result
    except Exception as e:
        logger.error(f"Error in multiply tool: {str(e)}")
        raise ToolError(f"Error multiplying numbers: {e}", "multiply")


def add_tool(a: int, b: int) -> int:
    """Add two numbers."""
    logger.debug(f"Executing add tool: {a} + {b}")
    try:
        result = a + b
        logger.info(f"Add result: {a} + {b} = {result}")
        return result
    except Exception as e:
        logger.error(f"Error in add tool: {str(e)}")
        raise ToolError(f"Error adding numbers: {e}", "add")


def subtract_tool(a: int, b: int) -> int:
    """Subtract two numbers."""
    logger.debug(f"Executing subtract tool: {a} - {b}")
    try:
        result = a - b
        logger.info(f"Subtract result: {a} - {b} = {result}")
        return result
    except Exception as e:
        logger.error(f"Error in subtract tool: {str(e)}")
        raise ToolError(f"Error subtracting numbers: {e}", "subtract")


# Available tools registry
AVAILABLE_TOOLS = {
    "multiply": multiply_tool,
    "add": add_tool,
    "subtract": subtract_tool,
}


@router.post("/multiply", response_model=ToolResponse)
async def execute_multiply(request: ToolRequest) -> ToolResponse:
    """Execute the multiply tool."""
    start_time = time.time()
    
    try:
        # Validate parameters
        if "a" not in request.parameters or "b" not in request.parameters:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Missing required parameters: 'a' and 'b'",
                    error_code="VALIDATION_ERROR",
                    details={"required_parameters": ["a", "b"]}
                ).dict()
            )
        
        a = int(request.parameters["a"])
        b = int(request.parameters["b"])
        
        logger.info(f"Executing multiply tool with a={a}, b={b}")
        result = multiply_tool(a, b)
        
        execution_time = time.time() - start_time
        
        return ToolResponse(
            result=result,
            status="success",
            tool_name="multiply",
            execution_time=execution_time
        )
    
    except ValueError as e:
        logger.error(f"ValueError in multiply tool: {e}")
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=f"Invalid input: {str(e)}",
                error_code="VALIDATION_ERROR",
                details={"tool_name": "multiply"}
            ).dict()
        )
    
    except ToolError as e:
        logger.error(f"ToolError in multiply tool: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=str(e),
                error_code="TOOL_ERROR",
                details={"tool_name": "multiply"}
            ).dict()
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in multiply tool: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                details={"tool_name": "multiply"}
            ).dict()
        )


@router.post("/add", response_model=ToolResponse)
async def execute_add(request: ToolRequest) -> ToolResponse:
    """Execute the add tool."""
    start_time = time.time()
    
    try:
        # Validate parameters
        if "a" not in request.parameters or "b" not in request.parameters:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Missing required parameters: 'a' and 'b'",
                    error_code="VALIDATION_ERROR",
                    details={"required_parameters": ["a", "b"]}
                ).dict()
            )
        
        a = int(request.parameters["a"])
        b = int(request.parameters["b"])
        
        logger.info(f"Executing add tool with a={a}, b={b}")
        result = add_tool(a, b)
        
        execution_time = time.time() - start_time
        
        return ToolResponse(
            result=result,
            status="success",
            tool_name="add",
            execution_time=execution_time
        )
    
    except ValueError as e:
        logger.error(f"ValueError in add tool: {e}")
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=f"Invalid input: {str(e)}",
                error_code="VALIDATION_ERROR",
                details={"tool_name": "add"}
            ).dict()
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in add tool: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                details={"tool_name": "add"}
            ).dict()
        )


@router.get("/", response_model=Dict[str, Any])
async def list_tools() -> Dict[str, Any]:
    """List all available tools."""
    return {
        "tools": list(AVAILABLE_TOOLS.keys()),
        "count": len(AVAILABLE_TOOLS),
        "descriptions": {
            "multiply": "Multiply two numbers",
            "add": "Add two numbers", 
            "subtract": "Subtract two numbers"
        }
    }


@router.get("/{tool_name}", response_model=Dict[str, Any])
async def get_tool_info(tool_name: str) -> Dict[str, Any]:
    """Get information about a specific tool."""
    if tool_name not in AVAILABLE_TOOLS:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=f"Tool '{tool_name}' not found",
                error_code="TOOL_NOT_FOUND",
                details={"available_tools": list(AVAILABLE_TOOLS.keys())}
            ).dict()
        )
    
    return {
        "name": tool_name,
        "description": f"{tool_name} tool",
        "available": True
    }

