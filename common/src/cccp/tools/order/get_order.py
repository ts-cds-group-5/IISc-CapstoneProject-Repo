"""Get Order Tool for CCCP Advanced.

This tool handles order retrieval with user authentication and validation.
"""

from typing import Dict, Any, Optional
from cccp.tools.base import BaseCCCPTool
from cccp.core.logging import get_logger
from cccp.core.exceptions import ToolError
from pydantic import BaseModel, Field
import json

logger = get_logger(__name__)


class GetOrderInput(BaseModel):
    """Input model for GetOrderTool."""
    order_id: str = Field(..., description="The order ID to retrieve")
    user_id: str = Field(..., description="The user ID for authentication")


class GetOrderTool(BaseCCCPTool):
    """Tool for retrieving order information with authentication and validation."""
    
    def __init__(self, **kwargs):
        """Initialize the GetOrderTool."""
        super().__init__(**kwargs)
    
    def _get_name(self) -> str:
        """Get the tool name."""
        return "get_order"
    
    def _get_description(self) -> str:
        """Get the tool description."""
        return "Retrieve order information by order ID with user authentication and validation"
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate tool inputs."""
        order_id = kwargs.get("order_id")
        user_id = kwargs.get("user_id")
        
        if not order_id or not user_id:
            raise ToolError("order_id and user_id are required")
        
        if not isinstance(order_id, str) or not isinstance(user_id, str):
            raise ToolError("order_id and user_id must be strings")
        
        return {"order_id": order_id, "user_id": user_id}
    
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool logic."""
        return self._run(kwargs.get("order_id", ""), kwargs.get("user_id", ""), **kwargs)
    
    def run(self, order_id: str, user_id: str, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            # Validate input
            if not order_id or not user_id:
                raise ToolError("order_id and user_id are required")
            
            # Authenticate user
            if not self._authenticate_user(user_id):
                raise ToolError(f"User {user_id} is not authenticated")
            
            # Validate order ID format
            if not self._validate_order_id(order_id):
                raise ToolError(f"Invalid order ID format: {order_id}")
            
            # Check if user owns the order
            if not self._check_order_ownership(order_id, user_id):
                raise ToolError(f"User {user_id} does not have access to order {order_id}")
            
            # Retrieve order from database
            order_details = self._fetch_order_from_db(order_id)
            
            if not order_details:
                raise ToolError(f"Order {order_id} not found")
            
            # Format response
            return self._format_order_response(order_details)
            
        except ToolError as e:
            logger.error(f"Tool error in get_order: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_order: {str(e)}")
            raise ToolError(f"Unexpected error: {str(e)}")
    
    def _authenticate_user(self, user_id: str) -> bool:
        """Authenticate the user."""
        try:
            # TODO: Implement actual user authentication
            # For now, accept any non-empty user_id
            if not user_id or user_id.strip() == "":
                return False
            
            # Mock authentication - in real implementation, check against user database
            logger.info(f"Authenticating user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Authentication error for user {user_id}: {str(e)}")
            return False
    
    def _validate_order_id(self, order_id: str) -> bool:
        """Validate order ID format."""
        try:
            # Basic validation - order ID should be alphanumeric and 5-10 characters
            if not order_id or len(order_id) < 5 or len(order_id) > 10:
                return False
            
            if not order_id.isalnum():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Order ID validation error: {str(e)}")
            return False
    
    def _check_order_ownership(self, order_id: str, user_id: str) -> bool:
        """Check if user owns the order."""
        try:
            # TODO: Implement actual ownership check against database
            # For now, simulate ownership check
            logger.info(f"Checking ownership: user {user_id} for order {order_id}")
            
            # Mock ownership check - in real implementation, query database
            # For demo purposes, accept if user_id contains "user" and order_id contains "order"
            return "user" in user_id.lower() and "order" in order_id.lower()
            
        except Exception as e:
            logger.error(f"Ownership check error: {str(e)}")
            return False
    
    def _fetch_order_from_db(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Fetch order details from database."""
        try:
            # TODO: Implement actual database query
            # For now, return mock data
            logger.info(f"Fetching order {order_id} from database")
            
            # Mock order data
            mock_orders = {
                "order123": {
                    "order_id": "order123",
                    "user_id": "user123",
                    "status": "shipped",
                    "total": 99.99,
                    "items": [
                        {"name": "Widget A", "quantity": 2, "price": 29.99},
                        {"name": "Widget B", "quantity": 1, "price": 39.99}
                    ],
                    "shipping_address": "123 Main St, City, State 12345",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-16T14:20:00Z"
                },
                "order456": {
                    "order_id": "order456",
                    "user_id": "user456",
                    "status": "delivered",
                    "total": 149.99,
                    "items": [
                        {"name": "Gadget X", "quantity": 1, "price": 149.99}
                    ],
                    "shipping_address": "456 Oak Ave, Town, State 67890",
                    "created_at": "2024-01-10T09:15:00Z",
                    "updated_at": "2024-01-12T16:45:00Z"
                }
            }
            
            return mock_orders.get(order_id)
            
        except Exception as e:
            logger.error(f"Database fetch error for order {order_id}: {str(e)}")
            return None
    
    def _format_order_response(self, order_details: Dict[str, Any]) -> str:
        """Format order details for response."""
        try:
            response = f"""Order Details:
Order ID: {order_details['order_id']}
Status: {order_details['status'].title()}
Total: ${order_details['total']:.2f}
Created: {order_details['created_at']}
Updated: {order_details['updated_at']}

Items:
"""
            
            for item in order_details['items']:
                response += f"- {item['name']} x{item['quantity']} @ ${item['price']:.2f}\n"
            
            response += f"\nShipping Address: {order_details['shipping_address']}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting order response: {str(e)}")
            return f"Order found but error formatting details: {str(e)}"
    
    def arun(self, order_id: str, user_id: str, **kwargs) -> str:
        """Run the tool asynchronously."""
        # For now, just delegate to the synchronous version
        return self.run(order_id, user_id, **kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary."""
        return {
            "name": self._get_name(),
            "description": self._get_description(),
            "tool_name": self.tool_name,
            "inputs": ["order_id", "user_id"],
            "outputs": ["order_details"]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GetOrderTool':
        """Create a tool from a dictionary."""
        return cls(**data)
    
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> 'GetOrderTool':
        """Create a tool from a JSON string."""
        return cls.from_dict(json.loads(data))
