"""View Cart Tool - Display shopping cart contents."""

from typing import Dict, Any, List, Optional
from cccp.tools.base import BaseCCCPTool
from cccp.core.logging import get_logger
from cccp.core.exceptions import ToolError
from cccp.tools.order.cart_utils import (
    format_cart_display,
    get_or_create_cart
)
from pydantic import BaseModel, Field
import json

logger = get_logger(__name__)


class ViewCartInput(BaseModel):
    """Input model for ViewCartTool (no parameters needed)."""
    pass


class ViewCartTool(BaseCCCPTool):
    """Tool for viewing shopping cart contents."""
    
    inputs: List[str] = Field(default=[], description="No input parameters required")
    outputs: List[str] = Field(default=["cart_contents"], description="Cart contents")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("ViewCartTool initialized")
    
    def _get_name(self) -> str:
        """Get the tool name."""
        return "viewcart"
    
    def _get_description(self) -> str:
        """Get the tool description."""
        return "View current shopping cart contents. Use when user says 'show cart', 'view cart', 'my cart', 'what's in my cart', 'cart contents'"
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """No inputs to validate."""
        logger.debug("ViewCartTool: No inputs to validate")
        return {}
    
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool logic."""
        return self._run(**kwargs)
    
    def run(self, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            logger.info("ViewCartTool: Displaying cart contents")
            
            # Get cart from session (via kwargs)
            user_session = kwargs.get('user_session')
            cart = self._get_cart_from_session(user_session)
            
            # Format and return
            response = format_cart_display(cart)
            
            logger.info(f"ViewCartTool: Displayed cart with {cart.get('total_items', 0)} items")
            return response
            
        except Exception as e:
            logger.error(f"ViewCartTool: Unexpected error - {str(e)}", exc_info=True)
            raise ToolError(f"Unexpected error: {str(e)}")
    
    def _get_cart_from_session(self, user_session: Optional[Dict]) -> Dict[str, Any]:
        """Get cart from user session."""
        if not user_session:
            logger.warning("ViewCartTool: No user session available")
            return get_or_create_cart()
        
        cart = user_session.get('shopping_cart')
        if not cart:
            logger.info("ViewCartTool: No cart in session, returning empty cart")
            cart = get_or_create_cart()
        
        return cart
    
    def arun(self, **kwargs) -> str:
        """Run asynchronously."""
        return self.run(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary."""
        return {
            "name": self._get_name(),
            "description": self._get_description(),
            "tool_name": self.tool_name,
            "inputs": self.inputs,
            "outputs": self.outputs
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ViewCartTool':
        """Create a tool from a dictionary."""
        return cls(**data)
    
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> 'ViewCartTool':
        """Create a tool from a JSON string."""
        return cls.from_dict(json.loads(data))

