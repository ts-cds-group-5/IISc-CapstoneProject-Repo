"""Custom tool calling agent for CCCP Advanced."""

import json
import re
from typing import Dict, Any, Optional, List
from cccp.services.model_service import ModelService
from cccp.core.config import get_settings
from cccp.tools import get_tool, get_all_tools
from cccp.core.logging import get_logger

logger = get_logger(__name__)


class CustomToolCallingAgent:
    """Custom tool calling agent that works with text-based models like Ollama and Phi-2."""
    
    def __init__(self):
        self.model_service = None
        self.available_tools = {}
        self._initialize_agent()
        logger.info("CustomToolCallingAgent initialized")
    
    def _initialize_agent(self):
        """Initialize the agent with model service and available tools."""
        try:
            settings = get_settings()
            self.model_service = ModelService(model_type=settings.model_type)
            
            # Get all available tools
            self.available_tools = {tool.name: tool for tool in get_all_tools()}
            logger.info(f"Initialized with tools: {list(self.available_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CustomToolCallingAgent: {str(e)}")
            raise
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and return structured response."""
        try:
            logger.info(f"Processing user input: {user_input}")
            
            # First, try to detect if this is a tool usage request
            tool_detection = self._detect_tool_usage(user_input)
            if tool_detection:
                return self._handle_tool_usage(tool_detection)
            
            # Otherwise, handle as general chat
            return self._handle_general_chat(user_input)
            
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            return {
                "intent": "error",
                "response": f"Error processing request: {str(e)}",
                "error": str(e)
            }
    
    def _detect_tool_usage(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Detect if user input is requesting a tool usage."""
        user_input_lower = user_input.lower()
        
        # Check for math operations (existing pattern matching)
        math_patterns = {
            'add': r'add\s+(\d+)\s*(?:and|by|with)?\s*(\d+)',
            'multiply': r'multiply\s+(\d+)\s*(?:and|by|with)?\s*(\d+)'
        }
        
        for operation, pattern in math_patterns.items():
            match = re.search(pattern, user_input_lower)
            if match:
                return {
                    "tool_name": operation,
                    "parameters": {
                        "a": int(match.group(1)),
                        "b": int(match.group(2))
                    },
                    "confidence": 0.95
                }
        
        # Check for other tool keywords
        tool_keywords = {
            'order': ['order', 'purchase', 'buy'],
            'get_order': ['my order', 'order status', 'order details']
        }
        
        for tool_name, keywords in tool_keywords.items():
            for keyword in keywords:
                if keyword in user_input_lower:
                    return {
                        "tool_name": tool_name,
                        "parameters": self._extract_parameters(user_input, tool_name),
                        "confidence": 0.8
                    }
        
        return None
    
    def _extract_parameters(self, user_input: str, tool_name: str) -> Dict[str, Any]:
        """Extract parameters for tool usage from user input."""
        # Simple parameter extraction - can be enhanced
        if tool_name == 'get_order':
            # Look for order ID patterns
            order_id_match = re.search(r'order[_\s]*id[:\s]*(\w+)', user_input.lower())
            if order_id_match:
                return {"order_id": order_id_match.group(1)}
        
        return {}
    
    def _handle_tool_usage(self, tool_detection: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool usage request."""
        try:
            tool_name = tool_detection["tool_name"]
            parameters = tool_detection["parameters"]
            
            logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")
            
            # Get and execute the tool
            tool = get_tool(tool_name)
            if not tool:
                return {
                    "intent": "error",
                    "response": f"Tool '{tool_name}' not found",
                    "tool_name": tool_name
                }
            
            # Execute the tool
            result = tool.run(**parameters)
            
            # Generate a natural language response
            response_text = self._generate_tool_response(tool_name, parameters, result)
            
            return {
                "intent": "tool_usage",
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result,
                "response": response_text,
                "confidence": tool_detection.get("confidence", 0.8)
            }
            
        except Exception as e:
            logger.error(f"Error executing tool: {str(e)}")
            return {
                "intent": "error",
                "response": f"Error executing tool: {str(e)}",
                "tool_name": tool_detection.get("tool_name", "unknown")
            }
    
    def _generate_tool_response(self, tool_name: str, parameters: Dict[str, Any], result: Any) -> str:
        """Generate a natural language response for tool execution."""
        if tool_name == 'add':
            a, b = parameters.get('a', 0), parameters.get('b', 0)
            return f"The result of adding {a} and {b} is {result}"
        elif tool_name == 'multiply':
            a, b = parameters.get('a', 0), parameters.get('b', 0)
            return f"The result of multiplying {a} and {b} is {result}"
        elif tool_name == 'get_order':
            order_id = parameters.get('order_id', 'unknown')
            return f"Order {order_id} details: {result}"
        else:
            return f"Tool '{tool_name}' executed successfully. Result: {result}"
    
    def _handle_general_chat(self, user_input: str) -> Dict[str, Any]:
        """Handle general chat using the model."""
        try:
            model = self.model_service.get_model()
            
            # Create a prompt for the model
            prompt = self._create_chat_prompt(user_input)
            
            # Generate response
            response = model.generate(prompt)
            
            # Clean up the response
            clean_response = self._clean_model_response(response, prompt)
            
            return {
                "intent": "general_chat",
                "response": clean_response,
                "confidence": 0.7
            }
            
        except Exception as e:
            logger.error(f"Error in general chat: {str(e)}")
            return {
                "intent": "error",
                "response": f"Error generating chat response: {str(e)}"
            }
    
    def _create_chat_prompt(self, user_input: str) -> str:
        """Create a prompt for general chat."""
        return f"""You are a helpful AI assistant. Please respond to the user's question or request in a friendly and helpful manner.

User: {user_input}

Assistant:"""
    
    def _clean_model_response(self, response: str, prompt: str) -> str:
        """Clean up the model response by removing the prompt if included."""
        if prompt in response:
            clean_response = response.replace(prompt, "").strip()
        else:
            clean_response = response.strip()
        
        # Remove any remaining prompt artifacts
        clean_response = re.sub(r'^(User:|Assistant:).*$', '', clean_response, flags=re.MULTILINE)
        
        return clean_response.strip()
    
    def parse_response(self, llm_output: str) -> Dict[str, Any]:
        """Parse LLM JSON output for structured tool calls."""
        try:
            # Try to extract JSON from the output
            json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                return parsed
            else:
                # Fallback to text-based parsing
                return self._parse_text_response(llm_output)
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, falling back to text parsing")
            return self._parse_text_response(llm_output)
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text-based response when JSON parsing fails."""
        text_lower = text.lower()
        
        # Simple text-based intent detection
        if any(word in text_lower for word in ['add', 'plus', '+']):
            return {"intent": "tool_usage", "tool_name": "addtool"}
        elif any(word in text_lower for word in ['multiply', 'times', '*']):
            return {"intent": "tool_usage", "tool_name": "multiplytool"}
        else:
            return {"intent": "general_chat", "response": text}
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool with given parameters."""
        try:
            tool = get_tool(tool_name)
            if not tool:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            return tool.run(**parameters)
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise
    
    def handle_intent(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent classification and routing."""
        intent = intent_data.get("intent", "unknown")
        
        if intent == "tool_usage":
            return self._handle_tool_usage(intent_data)
        elif intent == "general_chat":
            return intent_data
        else:
            return {
                "intent": "error",
                "response": f"Unknown intent: {intent}"
            }
