"""Chat service for CCCP Advanced."""

from typing import Dict, Any, Optional
from cccp.core.logging import LoggerMixin
from cccp.core.exceptions import ModelError, ToolError
from cccp.models.phi2_model import get_model_instance


class ChatService(LoggerMixin):
    """Service for handling chat operations."""
    
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the model."""
        try:
            self.model = get_model_instance()
            self.logger.info("Chat service initialized with model")
        except Exception as e:
            self.logger.error(f"Failed to initialize model: {str(e)}")
            raise ModelError(f"Failed to initialize model: {str(e)}")
    
    def create_task_template(self, instruction: str) -> str:
        """Create a structured task template."""
        self.logger.info(f"Creating task template for instruction: {instruction}")
        task_template = """You are a friendly chatbot assistant that gives structured output.
Your role is to arrange the given task in this structure.
### instruction:
{instruction}

Output:###Response:
"""
        return task_template.format(instruction=instruction)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response using the model."""
        if not self.model:
            raise ModelError("Model not initialized")
        
        try:
            self.logger.info(f"Generating response for prompt: {prompt}")
            
            # Create formatted prompt
            formatted_prompt = self.create_task_template(prompt)
            
            # Generate response
            response = self.model.generate(formatted_prompt, **kwargs)
            
            # Extract the response part
            if "Output:###Response:" in response:
                clean_response = response.split("Output:###Response:")[-1].strip()
                self.logger.debug(f"Extracted clean response: {clean_response}")
                return clean_response
            else:
                return response
                
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise ModelError(f"Error generating response: {str(e)}")
    
    def is_ready(self) -> bool:
        """Check if the chat service is ready."""
        return self.model is not None and self.model.is_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self.model:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_name": self.model.model_name,
            "device": self.model.device,
            "is_loaded": self.model.is_loaded
        }

