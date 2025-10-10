"""Remove from Cart Tool - Remove products from shopping cart."""

from typing import Dict, Any, List, Optional
from cccp.tools.base import BaseCCCPTool
from cccp.core.logging import get_logger
from cccp.core.exceptions import ToolError
from cccp.tools.order.cart_utils import (
    remove_item_from_cart,
    format_cart_summary,
    get_or_create_cart
)
from pydantic import BaseModel, Field
import json

logger = get_logger(__name__)


class RemoveFromCartInput(BaseModel):
    """Input model for RemoveFromCartTool."""
    product_name: str = Field(..., description="Product name to remove from cart")


class RemoveFromCartTool(BaseCCCPTool):
    """Tool for removing products from shopping cart."""
    
    inputs: List[str] = Field(default=["product_name"], description="Product name to remove")
    outputs: List[str] = Field(default=["cart_status"], description="Updated cart status")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("RemoveFromCartTool initialized")
    
    def _get_name(self) -> str:
        """Get the tool name."""
        return "removefromcart"
    
    def _get_description(self) -> str:
        """Get the tool description."""
        return "Remove a product from shopping cart. Use when user says 'remove [product]', 'delete [product]', 'take out [product] from cart'"
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate tool inputs."""
        logger.debug(f"RemoveFromCartTool: Validating inputs - {kwargs}")
        
        product_name = kwargs.get('product_name')
        if not product_name:
            raise ToolError("product_name is required")
        
        if not isinstance(product_name, str) or len(product_name.strip()) < 2:
            raise ToolError("product_name must be at least 2 characters")
        
        return {'product_name': product_name.strip()}
    
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool logic."""
        return self._run(**kwargs)
    
    def run(self, product_name: str, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            # Validate inputs
            validated = self._validate_inputs(product_name=product_name)
            product_name = validated['product_name']
            
            logger.info(f"RemoveFromCartTool: Removing {product_name} from cart")
            
            # Get cart from session (via kwargs)
            user_session = kwargs.get('user_session')
            cart = self._get_cart_from_session(user_session)
            
            # Remove from cart
            try:
                cart, remove_message = remove_item_from_cart(cart, product_name)
                
                # Save cart back to session
                self._save_cart_to_session(cart, user_session)
                
                # Format response
                cart_summary = format_cart_summary(cart)
                
                response = f"""{remove_message}

🛒 {cart_summary}"""
                
                logger.info(f"RemoveFromCartTool: Successfully removed item. Cart now has {cart['total_items']} items")
                return response
                
            except ValueError as e:
                logger.warning(f"RemoveFromCartTool: Validation error - {str(e)}")
                raise ToolError(str(e))
            
        except ToolError as e:
            logger.error(f"RemoveFromCartTool: Tool error - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"RemoveFromCartTool: Unexpected error - {str(e)}", exc_info=True)
            raise ToolError(f"Unexpected error: {str(e)}")
    
    def _get_cart_from_session(self, user_session: Optional[Dict]) -> Dict[str, Any]:
        """Get cart from user session."""
        if not user_session:
            logger.warning("RemoveFromCartTool: No user session available")
            return get_or_create_cart()
        
        cart = user_session.get('shopping_cart')
        if not cart:
            logger.info("RemoveFromCartTool: No cart in session")
            cart = get_or_create_cart()
        
        return cart
    
    def _save_cart_to_session(self, cart: Dict[str, Any], user_session: Optional[Dict]) -> None:
        """Save cart to user session."""
        if user_session is not None:
            user_session['shopping_cart'] = cart
            logger.debug("RemoveFromCartTool: Cart saved to session")
        else:
            logger.warning("RemoveFromCartTool: Cannot save cart - no session available")
    
    def arun(self, product_name: str, **kwargs) -> str:
        """Run asynchronously."""
        return self.run(product_name, **kwargs)
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'RemoveFromCartTool':
        """Create a tool from a dictionary."""
        return cls(**data)
    
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> 'RemoveFromCartTool':
        """Create a tool from a JSON string."""
        return cls.from_dict(json.loads(data))

