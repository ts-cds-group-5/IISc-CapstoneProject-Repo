"""Custom tool calling agent for CCCP Advanced."""

import json
import re
from typing import Dict, Any, Optional, List
from cccp.services.model_service import ModelService
from cccp.core.config import get_settings
from cccp.tools import get_tool, get_all_tools
from cccp.core.logging import get_logger
from cccp.prompts import get_prompt

logger = get_logger(__name__)


class CustomToolCallingAgent:
    """Custom tool calling agent that works with text-based models like Ollama and Phi-2."""
    
    def __init__(self):
        self.model_service = None
        self.available_tools = {}
        self.user_session = None  # Store user information
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
    
    def _get_tools_info(self) -> str:
        """
        Get formatted information about available tools for LLM prompt.
        
        Returns:
            Formatted string with tool names, descriptions, and parameters
        """
        tools_info = []
        
        for tool_name, tool_instance in self.available_tools.items():
            tool_info = f"""Tool: {tool_name}
Description: {tool_instance.description}
Parameters: {self._get_tool_parameters(tool_instance)}"""
            tools_info.append(tool_info.strip())
        
        return "\n\n".join(tools_info)
    
    def _get_tool_parameters(self, tool_instance) -> str:
        """
        Get parameter information for a specific tool.
        
        Args:
            tool_instance: The tool instance to extract parameters from
            
        Returns:
            Formatted string describing tool parameters
        """
        # Extract parameters from tool's run method signature
        import inspect
        sig = inspect.signature(tool_instance.run)
        params = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else 'any'
            param_default = f" (default: {param.default})" if param.default != inspect.Parameter.empty else " (required)"
            params.append(f"{param_name}: {param_type}{param_default}")
        
        return ", ".join(params) if params else "No parameters"
    
    def _validate_and_clean_json(self, response: str) -> Dict[str, Any]:
        """
        Validate and clean JSON response from LLM (especially Llama 3.2).
        
        Args:
            response: Raw response string from LLM
            
        Returns:
            Parsed dictionary from JSON response
            
        Raises:
            ValueError: If no valid JSON found in response
        """
        try:
            # Remove common JSON artifacts
            cleaned = response.strip()
            cleaned = cleaned.replace('```json', '').replace('```', '').strip()
            
            # Try to find JSON object
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = cleaned[start:end]
                parsed = json.loads(json_str)
                logger.debug(f"Successfully parsed JSON: {parsed}")
                return parsed
            else:
                raise ValueError("No valid JSON found in response")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON validation failed: {str(e)}")
            raise ValueError(f"Invalid JSON: {str(e)}")
    
    def process_user_input(self, user_input: str, user_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process user input and return structured response.
        
        Args:
            user_input: The user's input message
            user_info: Optional dict with pre-registered user info (user_id, name, mobile, email)
        """
        try:
            logger.info(f"Processing user input: {user_input}")
            
            # If user_info is provided from UI, use it to initialize session
            if user_info and not self.user_session:
                logger.info("Initializing user session from provided user_info")
                self.user_session = {
                    'user_id': user_info.get('user_id', 'unknown'),
                    'name': user_info.get('name', 'User'),
                    'mobile': user_info.get('mobile', 'Not provided'),
                    'email': user_info.get('email', 'Not provided'),
                    'registered_at': self._get_current_timestamp()
                }
                logger.info(f"User session initialized: {self.user_session}")
            
            # Check if user needs to register first (only if no user_info provided and no session)
            if not self.user_session:
                registration_info = self._detect_user_registration(user_input)
                if registration_info:
                    return self._handle_user_registration(registration_info)
                else:
                    return self._request_user_registration()
            
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
        """
        Detect if user input is requesting a tool usage using LLM-based detection.
        
        This method uses the centralized prompt system to leverage LLM for natural
        language understanding. Falls back to regex patterns if LLM fails or has low confidence.
        
        Args:
            user_input: The user's query string
            
        Returns:
            Dictionary with tool_name, parameters, confidence, and reasoning if tool detected,
            None otherwise
        """
        try:
            # Get available tools information
            tools_info = self._get_tools_info()
            
            # Get prompt from centralized prompt system (uses v2_llama_optimized by default)
            prompt = get_prompt(
                "tool_detection",
                user_input=user_input,
                tools_info=tools_info
            )
            
            logger.debug(f"Generated tool detection prompt for input: {user_input}")
            
            # Get LLM response
            model = self.model_service.get_model()
            response = model.generate(prompt, temperature=0.1, max_tokens=200)
            
            logger.debug(f"LLM raw response: {response}")
            
            # Parse and validate JSON response
            tool_detection = self._validate_and_clean_json(response)
            
            # Check if a tool was detected and confidence is sufficient
            if tool_detection.get("tool_name") and tool_detection.get("confidence", 0) >= 0.7:
                logger.info(f"✅ LLM detected tool: {tool_detection['tool_name']} (confidence: {tool_detection.get('confidence')})")
                logger.info(f"Reasoning: {tool_detection.get('reasoning', 'N/A')}")
                return tool_detection
            else:
                logger.info(f"LLM returned no tool or low confidence, using fallback")
                return self._fallback_tool_detection(user_input)
            
        except Exception as e:
            logger.warning(f"⚠️ LLM tool detection failed: {str(e)}, falling back to regex")
            # Fallback to regex patterns for reliability
            return self._fallback_tool_detection(user_input)
    
    def _fallback_tool_detection(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Fallback regex-based tool detection (original implementation).
        
        This method contains the original regex patterns and serves as a reliable
        fallback when LLM-based detection fails or returns low confidence.
        
        Args:
            user_input: The user's query string
            
        Returns:
            Dictionary with tool_name, parameters, and confidence if tool detected,
            None otherwise
        """
        user_input_lower = user_input.lower()
        
        logger.debug(f"Using regex fallback for: {user_input}")
        
        # Check for math operations (original pattern matching)
        math_patterns = {
            'add': r'add\s+(\d+)\s*(?:and|by|with)?\s*(\d+)',
            'multiply': r'multiply\s+(\d+)\s*(?:and|by|with)?\s*(\d+)'
        }
        
        for operation, pattern in math_patterns.items():
            match = re.search(pattern, user_input_lower)
            if match:
                logger.info(f"✅ Regex detected tool: {operation} (fallback)")
                return {
                    "tool_name": operation,
                    "parameters": {
                        "a": int(match.group(1)),
                        "b": int(match.group(2))
                    },
                    "confidence": 0.95,
                    "reasoning": "Regex pattern match (fallback)"
                }
        
        # Check for other tool keywords (original keyword matching)
        tool_keywords = {
            'place_order': ['place order', 'purchase', 'buy'],
            'getorder': ['cart','my cart','my cart status', 'cart status', 'order', 'my order', 
                        'my order status','my shipment','shipment details', 'my shipment details',
                        'shipping details', 'tracking details','delivery details','invoice details',
                        'ETA','delayed','early','on time','late']
        }
        
        for tool_name, keywords in tool_keywords.items():
            for keyword in keywords:
                if keyword in user_input_lower:
                    logger.info(f"✅ Regex detected tool: {tool_name} (fallback)")
                    return {
                        "tool_name": tool_name,
                        "parameters": self._extract_parameters(user_input, tool_name),
                        "confidence": 0.8,
                        "reasoning": f"Keyword match: '{keyword}' (fallback)"
                    }
        
        logger.debug("No tool detected by regex fallback")
        return None
    
    def _detect_user_registration(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Detect if user is providing registration information."""
        user_input_lower = user_input.lower()
        
        # Look for patterns that indicate user registration
        # Examples: "My user ID is 123", "I'm John Smith", "My mobile is 1234567890"
        
        registration_info = {}
        
        # Extract user ID
        user_id_patterns = [
            r'\b(?:user\s*id|userid|id)\s*[:\s]*([A-Za-z0-9]{3,20})\b',
            r'\bmy\s+(?:user\s*id|userid|id)\s+is\s+([A-Za-z0-9]{3,20})\b'
        ]
        
        for pattern in user_id_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                registration_info['user_id'] = match.group(1)
                break
        
        # Extract name
        name_patterns = [
            r'\b(?:i\s*am|my\s*name\s*is|name)\s+([A-Za-z\s]{2,30})\b',
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'  # First Last format
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, user_input)
            if match:
                registration_info['name'] = match.group(1).strip()
                break
        
        # Extract mobile number
        mobile_patterns = [
            r'\b(?:mobile|phone|number)\s*[:\s]*(\d{10,15})\b',
            r'\bmy\s+(?:mobile|phone|number)\s+is\s+(\d{10,15})\b',
            r'\b(\d{10,15})\b'  # Just numbers
        ]
        
        for pattern in mobile_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                registration_info['mobile'] = match.group(1)
                break
        
        # Extract email
        email_patterns = [
            r'\b(?:email|mail)\s*[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            r'\bmy\s+(?:email|mail)\s+is\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'  # Just email
        ]
        
        for pattern in email_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                registration_info['email'] = match.group(1)
                break
        
        # Return registration info if we found at least user_id
        if registration_info.get('user_id'):
            logger.info(f"Detected registration info: {registration_info}")
            return registration_info
        
        return None
    
    def _handle_user_registration(self, registration_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user registration process."""
        try:
            # Validate required fields
            user_id = registration_info.get('user_id')
            name = registration_info.get('name', 'User')
            mobile = registration_info.get('mobile', 'Not provided')
            email = registration_info.get('email', 'Not provided')
            
            if not user_id:
                return {
                    "intent": "registration_error",
                    "response": "I need your user ID to help you. Please provide your user ID, name, mobile number, and email.",
                    "error": "Missing user_id"
                }
            
            # Store user session
            self.user_session = {
                'user_id': user_id,
                'name': name,
                'mobile': mobile,
                'email': email,
                'registered_at': self._get_current_timestamp()
            }
            
            logger.info(f"User registered: {self.user_session}")
            
            # Generate personalized welcome message
            welcome_message = f"""Hello {name}! 👋 

I've registered you with:
- User ID: {user_id}
- Name: {name}
- Mobile: {mobile}
- Email: {email}

How can I help you today? You can ask me about:
- Your orders: "What happened to my order 454?"
- Order status: "Check my order status"
- Shipping details: "When will my order be delivered?"

What would you like to know?"""
            
            return {
                "intent": "registration_success",
                "response": welcome_message,
                "user_session": self.user_session
            }
            
        except Exception as e:
            logger.error(f"Error handling user registration: {str(e)}")
            return {
                "intent": "registration_error",
                "response": f"Sorry, there was an error registering you: {str(e)}",
                "error": str(e)
            }
    
    def _request_user_registration(self) -> Dict[str, Any]:
        """Request user registration information."""
        registration_message = """Welcome! 👋 I'm your customer service assistant.

To help you with your orders, I need some information from you. Please provide:

1. **Your User ID** (e.g., "My user ID is 12345")
2. **Your Name** (e.g., "I'm John Smith") 
3. **Your Mobile Number** (e.g., "My mobile is 9876543210")
4. **Your Email** (e.g., "My email is john@example.com")

You can provide all this information in one message, like:
"My user ID is 12345, I'm John Smith, my mobile is 9876543210, and my email is john@example.com"

Once you're registered, I can help you check your orders, track shipments, and more!"""
        
        return {
            "intent": "registration_request",
            "response": registration_message
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _extract_parameters(self, user_input: str, tool_name: str) -> Dict[str, Any]:
        """Extract parameters for tool usage from user input."""
        if tool_name == 'getorder':
            # Look for cart ID patterns
            cart_id_patterns = [
                r'\b(?:cart|Cart|CART)[\s#:]*([A-Za-z0-9]{1,15})\b',  # "cart 454", "Cart cart123"
                r'\bmy\s+cart[\s#:]*([A-Za-z0-9]{1,15})\b',           # "my cart 454"
                r'\bcart[_\s]*id[:\s]*([A-Za-z0-9]{1,15})\b',        # "cart id: 454", "cart_id: 123"
                r'\b(?:order|Order|ORDER)[\s#:]*([A-Za-z0-9]{1,15})\b',  # "cart 454", "Cart cart123",
                 r'\bmy\s+(?:order|Order|ORDER)[\s#:]*([A-Za-z0-9]{1,15})\b',                 
            ]
            
            for pattern in cart_id_patterns:
                cart_id_match = re.search(pattern, user_input, re.IGNORECASE)
                if cart_id_match:
                    cart_id = cart_id_match.group(1)
                    logger.info(f"Extracted cart ID: {cart_id} using pattern: {pattern}")
                    return {"cart_id": cart_id}
            
            # Look for email patterns
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, user_input)
            if email_match:
                customer_email = email_match.group(0)
                logger.info(f"Extracted customer email: {customer_email}")
                return {"customer_email": customer_email}
            
            # Look for name patterns (if user session has name, use it)
            if self.user_session and self.user_session.get('name'):
                customer_name = self.user_session['name']
                logger.info(f"Using customer name from session: {customer_name}")
                return {"customer_full_name": customer_name}
            
            logger.warning(f"Could not extract cart_id, email, or name from: {user_input}")
        
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
        # Get user name for personalized responses
        user_name = self.user_session.get('name', 'there') if self.user_session else 'there'
        
        if tool_name == 'add':
            a, b = parameters.get('a', 0), parameters.get('b', 0)
            return f"The result of adding {a} and {b} is {result}"
        elif tool_name == 'multiply':
            a, b = parameters.get('a', 0), parameters.get('b', 0)
            return f"The result of multiplying {a} and {b} is {result}"
        elif tool_name == 'getorder':
            # For getorder tool, just return the result directly (it's already formatted)
            return str(result)
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
