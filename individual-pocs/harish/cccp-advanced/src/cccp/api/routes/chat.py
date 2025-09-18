"""Chat routes for CCCP Advanced API."""

import re
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from langchain_community.llms import HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool

from cccp.core.logging import get_logger
from cccp.core.exceptions import ModelError, ToolError
from cccp.services.model_service import ModelService
#from cccp.models.phi2_model import get_model_instance
from cccp.api.models.requests import ChatRequest
from cccp.api.models.responses import ChatResponse, ErrorResponse
from cccp.services.chat_service import ChatService

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


# Tool definitions (moved from original server_api.py)
@tool
def multiply(a: int, b: int) -> int:
    """Multiplies two numbers and returns the result."""
    logger.debug(f"Inside multiply tool with a: {a}, b: {b} and types {type(a)}, {type(b)}")
    try:
        logger.info(f"Multiplying {a} and {b}")
        result = a * b  # Fixed: was a / b in original
    except Exception as e:
        logger.error(f"Error multiplying numbers: {e}")
        raise ToolError(f"Error multiplying numbers: {e}", "multiply")
    logger.info(f"Result of multiplying {a} and {b} is {result}")
    return result


def create_task_template(instruction: str) -> str:
    """Create a structured task template."""
    logger.info(f"Creating task template for instruction: {instruction}")
    task_template = """You are a friendly chatbot assistant that gives structured output.
Your role is to arrange the given task in this structure.
### instruction:
{instruction}

Output:###Response:
"""
    return task_template.format(instruction=instruction)


def detect_math_operation(prompt: str) -> Dict[str, Any]:
    """Detect if the prompt contains a math operation."""
    multiply_pattern = re.compile(
        r"multiply\s+(\d+)\s*(?:and|by|with)?\s*(\d+)", re.IGNORECASE
    )
    
    match = multiply_pattern.search(prompt)
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        logger.debug(f"Detected multiply operation: {a} * {b}")
        return {"operation": "multiply", "a": a, "b": b}
    
    return {"operation": None}


@router.post("/generate", response_model=ChatResponse)
async def generate_response(request: ChatRequest) -> ChatResponse:
    """Generate a response using the model."""
    start_time = time.time()
    
    try:
        logger.info(f"Received chat request: {request.prompt}")
        
        # Check for math operations first
        math_operation = detect_math_operation(request.prompt)
        
        if math_operation["operation"] == "multiply":
            # Use tool for math operations
            a = math_operation["a"]
            b = math_operation["b"]
            
            logger.info(f"Executing multiply tool: {a} * {b}")
            result = multiply.invoke({"a": a, "b": b})
            
            response_text = f"The result of multiplying {a} and {b} is {result}"
            
            execution_time = time.time() - start_time
            
            return ChatResponse(
                response=response_text,
                status="success",
                user_id=request.user_id,
                tool_used="multiply",
                metadata={
                    "execution_time": execution_time,
                    "operation": "multiply",
                    "result": result
                }
            )
        
        else:
            # Use model for general chat
            logger.info("Using model for general chat")
            
            # Get model instance
#            model = get_model_instance()
            model_service = ModelService()
            model = model_service.get_model()
            
            # Create formatted prompt
            formatted_prompt = create_task_template(request.prompt)
            logger.debug(f"Formatted prompt: {formatted_prompt}")
            
            # Generate response using model
            generated_text = model.generate(formatted_prompt)
            logger.info(f"Generated response: {generated_text}")
            
            # Extract the response part
            if "Output:###Response:" in generated_text:
                response_text = generated_text.split("Output:###Response:")[-1].strip()
                logger.debug(f"Extracted response: {response_text}")
            else:
                response_text = generated_text
            
            execution_time = time.time() - start_time
            
            return ChatResponse(
                response=response_text,
                status="success",
                user_id=request.user_id,
                metadata={
                    "execution_time": execution_time,
                    "model_used": model.model_name
                }
            )
    
    except ModelError as e:
        logger.error(f"Model error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=str(e),
                error_code="MODEL_ERROR",
                details={"model_name": "microsoft/phi-2"}
            ).dict()
        )
    
    except ToolError as e:
        logger.error(f"Tool error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=str(e),
                error_code="TOOL_ERROR",
                details={"tool_name": e.tool_name}
            ).dict()
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR"
            ).dict()
        )


@router.get("/", response_model=Dict[str, str])
async def chat_info() -> Dict[str, str]:
    """Get chat service information."""
    return {
        "service": "CCCP Advanced Chat",
        "version": "0.1.0",
        "status": "active",
        "available_tools": "multiply"
    }

