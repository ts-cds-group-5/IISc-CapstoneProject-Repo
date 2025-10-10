"""Intent Classifier for CCCP Advanced.

This module provides intent classification capabilities for conversation chunks.
"""

from typing import Dict, List, Any, Optional
from cccp.core.logging import get_logger
from cccp.services.model_service import ModelService
import json
import re

logger = get_logger(__name__)


class IntentClassifier:
    """Intent classifier for conversation chunks."""
    
    def __init__(self):
        """Initialize the intent classifier."""
        self.model_service = ModelService()
        self.logger = get_logger(__name__)
        
        # Define intent categories
        self.intent_categories = [
            "order_inquiry",
            "catalog_inquiry",
            "general_chat", 
            "tool_usage",
            "complaint",
            "support_request",
            "billing_inquiry",
            "other"
        ]
        
        # Create classification prompt
        self.classification_prompt = self._create_classification_prompt()
        
        self.logger.info("IntentClassifier initialized")
    
    def _create_classification_prompt(self) -> str:
        """Create the intent classification prompt."""
        return f"""You are an intent classification system. Analyze conversation chunks and classify the user's intent.

Intent Categories:
- order_inquiry: Questions about orders, order status, order details
- catalog_inquiry: Questions about available products, collections, catalog, product search, what's in stock
- general_chat: General conversation, greetings, small talk
- tool_usage: Requests to use specific tools or perform calculations
- complaint: Complaints about service, products, or experience
- support_request: Requests for technical support or help
- billing_inquiry: Questions about billing, payments, refunds
- other: Anything that doesn't fit the above categories

Respond with JSON format:
{{
    "intent": "order_inquiry",
    "entities": {{
        "order_id": "12345",
        "time_reference": "yesterday",
        "user_id": "user123"
    }},
    "confidence": 0.88,
    "suggested_tools": ["get_order", "get_user_orders"],
    "reasoning": "User is asking about order status with specific order ID"
}}

Always respond with valid JSON."""
    
    def classify(self, conversation_chunk: str) -> Dict[str, Any]:
        """Classify intent from conversation chunk."""
        try:
            self.logger.info(f"Classifying intent for: {conversation_chunk[:100]}...")
            
            # Create full prompt
            prompt = f"{self.classification_prompt}\n\nConversation: {conversation_chunk}\n\nClassification:"
            
            # Get model response
            model = self.model_service.get_model()
            response = model.generate(prompt)
            
            # Parse response
            parsed_response = self._parse_response(response)
            
            # Validate and enhance response
            result = self._validate_and_enhance(parsed_response, conversation_chunk)
            
            self.logger.info(f"Intent classified as: {result['intent']} (confidence: {result['confidence']})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error classifying intent: {str(e)}")
            return {
                "intent": "error",
                "entities": {},
                "confidence": 0.0,
                "suggested_tools": [],
                "reasoning": f"Classification error: {str(e)}",
                "error": str(e)
            }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse model response to extract JSON."""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Fallback: create basic classification
                return {
                    "intent": "general_chat",
                    "entities": {},
                    "confidence": 0.5,
                    "suggested_tools": [],
                    "reasoning": "Could not parse structured response"
                }
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON from response: {e}")
            return {
                "intent": "general_chat",
                "entities": {},
                "confidence": 0.5,
                "suggested_tools": [],
                "reasoning": f"JSON parsing error: {str(e)}"
            }
    
    def _validate_and_enhance(self, parsed_response: Dict[str, Any], conversation_chunk: str) -> Dict[str, Any]:
        """Validate and enhance the classification result."""
        try:
            # Validate intent category
            intent = parsed_response.get("intent", "general_chat")
            if intent not in self.intent_categories:
                intent = "other"
            
            # Validate confidence score
            confidence = parsed_response.get("confidence", 0.5)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                confidence = 0.5
            
            # Extract entities from conversation if not provided
            entities = parsed_response.get("entities", {})
            if not entities:
                entities = self._extract_entities(conversation_chunk)
            
            # Get suggested tools based on intent
            suggested_tools = parsed_response.get("suggested_tools", [])
            if not suggested_tools:
                suggested_tools = self._get_suggested_tools(intent)
            
            return {
                "intent": intent,
                "entities": entities,
                "confidence": confidence,
                "suggested_tools": suggested_tools,
                "reasoning": parsed_response.get("reasoning", "No reasoning provided"),
                "raw_response": parsed_response
            }
            
        except Exception as e:
            self.logger.error(f"Error validating classification: {str(e)}")
            return {
                "intent": "error",
                "entities": {},
                "confidence": 0.0,
                "suggested_tools": [],
                "reasoning": f"Validation error: {str(e)}",
                "error": str(e)
            }
    
    def _extract_entities(self, conversation_chunk: str) -> Dict[str, str]:
        """Extract entities from conversation chunk."""
        entities = {}
        
        # Extract order IDs (simple pattern matching)
        order_id_pattern = r'\b(?:order|Order|ORDER)[\s#:]*([A-Za-z0-9]{5,10})\b'
        order_matches = re.findall(order_id_pattern, conversation_chunk)
        if order_matches:
            entities["order_id"] = order_matches[0]
        
        # Extract user IDs (simple pattern matching)
        user_id_pattern = r'\b(?:user|User|USER)[\s#:]*([A-Za-z0-9]{3,20})\b'
        user_matches = re.findall(user_id_pattern, conversation_chunk)
        if user_matches:
            entities["user_id"] = user_matches[0]
        
        # Extract time references
        time_patterns = [
            r'\b(?:yesterday|today|tomorrow)\b',
            r'\b(?:last|this|next)\s+(?:week|month|year)\b',
            r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
        ]
        for pattern in time_patterns:
            if re.search(pattern, conversation_chunk, re.IGNORECASE):
                entities["time_reference"] = re.search(pattern, conversation_chunk, re.IGNORECASE).group(0)
                break
        
        return entities
    
    def _get_suggested_tools(self, intent: str) -> List[str]:
        """Get suggested tools based on intent."""
        tool_mapping = {
            "order_inquiry": ["get_order", "get_user_orders"],
            "catalog_inquiry": ["listcollections", "getcatalog", "searchproducts"],
            "tool_usage": ["add", "multiply", "get_order"],
            "billing_inquiry": ["get_order", "get_user_orders"],
            "support_request": ["get_order", "get_user_orders"],
            "complaint": ["get_order", "get_user_orders"],
            "general_chat": [],
            "other": []
        }
        
        return tool_mapping.get(intent, [])
    
    def classify_batch(self, conversation_chunks: List[str]) -> List[Dict[str, Any]]:
        """Classify multiple conversation chunks."""
        results = []
        for chunk in conversation_chunks:
            result = self.classify(chunk)
            results.append(result)
        return results
    
    def get_intent_statistics(self, classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics from a batch of classifications."""
        if not classifications:
            return {}
        
        intent_counts = {}
        confidence_scores = []
        
        for classification in classifications:
            intent = classification.get("intent", "unknown")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            confidence_scores.append(classification.get("confidence", 0.0))
        
        return {
            "total_chunks": len(classifications),
            "intent_distribution": intent_counts,
            "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
            "most_common_intent": max(intent_counts.items(), key=lambda x: x[1])[0] if intent_counts else "unknown"
        }

