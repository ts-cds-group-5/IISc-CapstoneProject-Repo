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

#adding for Langgraph agentic application
from cccp.agents.workflows.nodes.chat_agent import create_chat_agent

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

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

@router.post("/generate", response_model=ChatResponse)
async def generate_response(request: ChatRequest) -> ChatResponse:
    """Generate a response using the model."""
    start_time = time.time()
    
    try:
        logger.info(f"Received chat request: {request.prompt}")
        logger.info("Using LangGraph agent for general chat")
            
        # Extract user info from request
        user_info = None
        if request.user_name or request.user_mobile or request.user_email:
            user_info = {
                "user_id": request.user_id,
                "name": request.user_name,
                "mobile": request.user_mobile,
                "email": request.user_email
            }
            logger.info(f"User info provided: {user_info}")
            
        # Create and invoke the agent
        agent = create_chat_agent()
        result = agent.invoke({
                "user_input": request.prompt,
                "user_info": user_info
            })
        response_text = result["response"]            
        
        logger.info(f"Generated response: {response_text}")
            
        execution_time = time.time() - start_time
            
        return ChatResponse(
                response=response_text,
                status="success",
                user_id=request.user_id,
                metadata={
                    "execution_time": execution_time,
                    "model_used": result.get("model_used", "langgraph_agent")
                }
        # # Check for math operations first
        # math_operation = detect_math_operation(request.prompt)
        
        # if math_operation["operation"] == "multiply":
        #     # Use tool for math operations
        #     a = math_operation["a"]
        #     b = math_operation["b"]
            
        #     logger.info(f"Executing multiply tool: {a} * {b}")
        #     result = multiply.invoke({"a": a, "b": b})
            
        #     response_text = f"The result of multiplying {a} and {b} is {result}"
        #     execution_time = time.time() - start_time
            
        #     return ChatResponse(
        #         response=response_text,
        #         status="success",
        #         user_id=request.user_id,
        #         tool_used="multiply",
        #         metadata={
        #             "execution_time": execution_time,
        #             "operation": "multiply",
        #             "result": result
        #         }
        #     )
        
        # elif math_operation["operation"] == "add":
        #     a = math_operation["a"]
        #     b = math_operation["b"]
        #     logger.info(f"Executing add tool: {a} + {b}")
        #     result = add.invoke({"a": a, "b": b})
        #     response_text = f"The result of (sq)adding {a} and {b} is {result}"
        #     execution_time = time.time() - start_time
            
        #     return ChatResponse(
        #         response=response_text,
        #         status="success",
        #         user_id=request.user_id,
        #         tool_used="add",
        #         metadata={
        #             "execution_time": execution_time,
        #             "operation": "add",
        #             "result": result
        #         }
        #     )
        
        # elif math_operation["operation"] == "subtract":
        #     a = math_operation["a"]
        #     b = math_operation["b"]
        #     logger.info(f"Executing subtract tool: {a} - {b}")
        #     result = subtract.invoke({"a": a, "b": b})
        #     response_text = f"The result of subtracting {a} and {b} is {result}"
        #     execution_time = time.time() - start_time
            
        #     return ChatResponse(
        #         response=response_text,
        #         status="success",
        #         user_id=request.user_id,
        #         tool_used="subtract",
        #         metadata={
        #             "execution_time": execution_time,
        #             "operation": "subtract",
        #             "result": result
        #         }
        #     )
        
#        else:
            # Use LangGraph agent for general chat
            # logger.info("Using LangGraph agent for general chat")
            #
            # # Create and invoke the agent
            # agent = create_chat_agent()
            # result = agent.invoke({
            #     "user_input": request.prompt, 
            #     "messages": []
            # })
            # response_text = result["response"]
            #
            # logger.info(f"Generated response: {response_text}")
#            
#            prior code for model based chat ***
#             # Use model for general chat
#             logger.info("Using model for general chat")
            
#             # Get model instance
# #            model = get_model_instance()
#             model_service = ModelService()
#             model = model_service.get_model()
            
#             # Create formatted prompt
#             formatted_prompt = create_task_template(request.prompt)
#             logger.debug(f"Formatted prompt: {formatted_prompt}")
            
#             # Generate response using model
#             generated_text = model.generate(formatted_prompt)
#             logger.info(f"Generated response: {generated_text}")
            
#             # Extract the response part
#             if "Output:###Response:" in generated_text:
#                 response_text = generated_text.split("Output:###Response:")[-1].strip()
#                 logger.debug(f"Extracted response: {response_text}")
#             else:
#                 response_text = generated_text


            ) # end of chat response
    
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
        "available_tools": "multiply" #@todo: check if this is needed
    }

