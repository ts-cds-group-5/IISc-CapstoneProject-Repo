"""Clear Cart Tool - Clear all items from shopping cart."""

from typing import Dict, Any, List, Optional
from cccp.tools.base import BaseCCCPTool
from cccp.core.logging import get_logger
from cccp.core.exceptions import ToolError
from pydantic import BaseModel, Field
import json

logger = get_logger(__name__)


class ClearCartInput(BaseModel):
    """Input model for ClearCartTool (no parameters needed)."""
    pass


class ClearCartTool(BaseCCCPTool):
    """Tool for clearing all items from shopping cart."""
    
    inputs: List[str] = Field(default=[], description="No input parameters required")
    outputs: List[str] = Field(default=["status"], description="Clear status message")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("ClearCartTool initialized")
    
    def _get_name(self) -> str:
        """Get the tool name."""
        return "clearcart"
    
    def _get_description(self) -> str:
        """Get the tool description."""
        return "Clear all items from shopping cart. Use when user says 'clear cart', 'empty cart', 'delete cart', 'cancel cart', 'reset cart'"
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """No inputs to validate."""
        logger.debug("ClearCartTool: No inputs to validate")
        return {}
    
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool logic."""
        return self._run(**kwargs)
    
    def run(self, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            logger.info("ClearCartTool: Clearing cart")
            
            # Clear cart from session (via kwargs)
            user_session = kwargs.get('user_session')
            self._clear_cart_from_session(user_session)
            
            response = """🗑️  Cart cleared.

Your shopping cart is now empty.

Browse our catalog and add items anytime:
• 'What collections do you have?'
• 'Show me Books'
• 'Find laptops'"""
            
            logger.info("ClearCartTool: Cart cleared successfully")
            return response
            
        except Exception as e:
            logger.error(f"ClearCartTool: Unexpected error - {str(e)}", exc_info=True)
            raise ToolError(f"Unexpected error: {str(e)}")
    
    def _clear_cart_from_session(self, user_session: Optional[Dict]) -> None:
        """Clear cart from user session."""
        if user_session and 'shopping_cart' in user_session:
            del user_session['shopping_cart']
            logger.debug("ClearCartTool: Cart removed from session")
        else:
            logger.warning("ClearCartTool: No session or cart to clear")
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'ClearCartTool':
        """Create a tool from a dictionary."""
        return cls(**data)
    
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> 'ClearCartTool':
        """Create a tool from a JSON string."""
        return cls.from_dict(json.loads(data))

