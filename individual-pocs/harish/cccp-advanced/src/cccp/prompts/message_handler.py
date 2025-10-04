"""Message handler for processing different types of messages."""

from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from cccp.core.logging import LoggerMixin
from .math_prompts import MathPromptTemplates

class MessageHandler(LoggerMixin):
    """Handles message processing and template selection."""
    
    def __init__(self):
        self.math_templates = MathPromptTemplates()
    
    def detect_message_type(self, user_input: str) -> str:
        """Detect the type of message to determine appropriate template."""
        user_input_lower = user_input.lower()
        
        # Math operations detection
        math_keywords = ['add', 'multiply', 'subtract', 'divide', 'calculate', 'math', '+', '*', '-', '/']
        if any(keyword in user_input_lower for keyword in math_keywords):
            return "math"
        
        # Default to general chat
        return "general"
    
    def create_messages(self, user_input: str, message_type: str = None) -> List[BaseMessage]:
        """Create appropriate messages based on input type."""
        if message_type is None:
            message_type = self.detect_message_type(user_input)
        
        self.logger.info(f"Creating messages for type: {message_type}")
        
        if message_type == "math":
            return self._create_math_messages(user_input)
        else:
            return self._create_general_messages(user_input)
    
    def _create_math_messages(self, user_input: str) -> List[BaseMessage]:
        """Create messages for math operations."""
        return self.math_templates.format_math_messages(user_input)
    
    def _create_general_messages(self, user_input: str) -> List[BaseMessage]:
        """Create messages for general chat."""
        system_prompt = """You are a helpful AI assistant. You can help with various tasks and have access to tools when needed.

When users ask questions:
1. Provide helpful and accurate responses
2. Use tools when appropriate for calculations or specific tasks
3. Be conversational and friendly
4. If you're unsure about something, say so rather than guessing"""
        
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
    
    def extract_response_content(self, response: BaseMessage) -> str:
        """Extract text content from response message."""
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
