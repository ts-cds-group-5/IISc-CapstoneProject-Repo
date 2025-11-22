"""Add to Cart Tool - Add products to shopping cart."""

from typing import Dict, Any, List, Optional
from cccp.tools.base import BaseCCCPTool
from cccp.core.logging import get_logger
from cccp.core.exceptions import ToolError
from cccp.tools.order.cart_utils import (
    get_or_create_cart,
    add_item_to_cart,
    format_cart_summary
)
from pydantic import BaseModel, Field
import json

logger = get_logger(__name__)


class AddToCartInput(BaseModel):
    """Input model for AddToCartTool."""
    product_name: str = Field(..., description="Product name to add to cart")
    quantity: int = Field(default=1, description="Quantity to add (default: 1)")


class AddToCartTool(BaseCCCPTool):
    """Tool for adding products to shopping cart."""
    
    inputs: List[str] = Field(
        default=["product_name", "quantity"],
        description="Product name (required) and quantity (optional)"
    )
    outputs: List[str] = Field(default=["cart_status"], description="Updated cart status")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("AddToCartTool initialized")
    
    def _get_name(self) -> str:
        """Get the tool name."""
        return "addtocart"
    
    def _get_description(self) -> str:
        """Get the tool description."""
        return "Add a product to shopping cart. Use when user says 'add [product]', 'buy [product]', 'I want [product]', 'get me [product]'"
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate tool inputs."""
        logger.debug(f"AddToCartTool: Validating inputs - {kwargs}")
        
        product_name = kwargs.get('product_name')
        if not product_name:
            raise ToolError("product_name is required")
        
        if not isinstance(product_name, str) or len(product_name.strip()) < 2:
            raise ToolError("product_name must be at least 2 characters")
        
        quantity = kwargs.get('quantity', 1)
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except (ValueError, TypeError) as e:
            raise ToolError(f"quantity must be a positive integer: {e}")
        
        return {
            'product_name': product_name.strip(),
            'quantity': quantity
        }
    
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool logic."""
        return self._run(**kwargs)
    
    def run(self, product_name: str, quantity: int = 1, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            # Validate inputs
            validated = self._validate_inputs(product_name=product_name, quantity=quantity)
            product_name = validated['product_name']
            quantity = validated['quantity']
            
            logger.info(f"AddToCartTool: Adding {product_name} × {quantity} to cart")
            
            # Search for product in database
            products = self._search_product(product_name)
            
            if not products:
                logger.warning(f"AddToCartTool: Product not found - {product_name}")
                return f"❌ Product '{product_name}' not found.\n\nTry browsing our catalog:\n- 'Show me Electronics'\n- 'List Books'\n- 'Show catalog'"
            
            if len(products) > 1:
                logger.info(f"AddToCartTool: Multiple products match '{product_name}'")
                return self._format_multiple_matches(products, product_name)
            
            product = products[0]
            logger.info(f"AddToCartTool: Found product - {product['product_name']}")
            
            # Get cart from session (via kwargs)
            user_session = kwargs.get('user_session')
            cart = self._get_cart_from_session(user_session)
            
            # Add to cart
            try:
                cart, add_message = add_item_to_cart(cart, product, quantity)
                
                # Save cart back to session
                self._save_cart_to_session(cart, user_session)
                
                # Format response
                cart_summary = format_cart_summary(cart)
                
                response = f"""{add_message}

🛒 {cart_summary}

Continue shopping or say 'checkout' to place order."""
                
                logger.info(f"AddToCartTool: Successfully added item. Cart now has {cart['total_items']} items")
                return response
                
            except ValueError as e:
                logger.warning(f"AddToCartTool: Validation error - {str(e)}")
                raise ToolError(str(e))
            
        except ToolError as e:
            logger.error(f"AddToCartTool: Tool error - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"AddToCartTool: Unexpected error - {str(e)}", exc_info=True)
            raise ToolError(f"Unexpected error: {str(e)}")
    
    def _search_product(self, product_name: str) -> List[Dict[str, Any]]:
        """Search for product in database."""
        try:
            import asyncio
            import threading
            
            result = None
            exception = None
            
            def run_async():
                nonlocal result, exception
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self._search_product_async(product_name))
                    logger.debug(f"AddToCartTool: Product search completed with {len(result) if result else 0} results")
                except Exception as e:
                    exception = e
                    logger.error(f"AddToCartTool: Product search failed - {str(e)}")
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
            
            return result or []
            
        except Exception as e:
            logger.error(f"AddToCartTool: Product search error - {str(e)}")
            return []
    
    async def _search_product_async(self, product_name: str) -> List[Dict[str, Any]]:
        """Async product search using MCP client."""
        from cccp.mcp.client import MCPPostgresClient
        
        client = MCPPostgresClient()
        try:
            await client.connect()
            logger.debug(f"AddToCartTool: Searching for product: {product_name}")
            
            # Search for product using ILIKE
            query = """
                SELECT 
                    product_id, product_name, product_description,
                    product_price, currency, product_stock_qty
                FROM g5_product
                WHERE product_name ILIKE $1
                AND product_stock_qty > 0
                ORDER BY product_name
            """
            
            params = {'1': f'%{product_name}%'}
            result = await client.query(query, params)
            logger.info(f"AddToCartTool: Found {len(result)} matching products")
            
            return result
            
        except Exception as e:
            logger.error(f"AddToCartTool: Database query error - {str(e)}")
            raise
        finally:
            await client.close()
    
    def _format_multiple_matches(self, products: List[Dict], search_term: str) -> str:
        """Format response when multiple products match."""
        lines = [f"Found {len(products)} products matching '{search_term}':\n"]
        
        for i, product in enumerate(products, 1):
            price = float(product['product_price'])
            stock = product['product_stock_qty']
            lines.append(f"{i}. {product['product_name']}")
            lines.append(f"   Price: ₹{price:,.2f} | Stock: {stock} available\n")
        
        lines.append("Please be more specific. Example: 'Add Samsung Galaxy' or 'Add Atomic Habits'")
        
        return "\n".join(lines)
    
    def _get_cart_from_session(self, user_session: Optional[Dict]) -> Dict[str, Any]:
        """Get cart from user session."""
        if not user_session:
            logger.warning("AddToCartTool: No user session available, creating empty cart")
            return get_or_create_cart()
        
        cart = user_session.get('shopping_cart')
        if not cart:
            logger.info("AddToCartTool: No cart in session, creating new one")
            cart = get_or_create_cart()
        
        return cart
    
    def _save_cart_to_session(self, cart: Dict[str, Any], user_session: Optional[Dict]) -> None:
        """Save cart to user session."""
        if user_session is not None:
            user_session['shopping_cart'] = cart
            logger.debug("AddToCartTool: Cart saved to session")
        else:
            logger.warning("AddToCartTool: Cannot save cart - no session available")
    
    def arun(self, product_name: str, quantity: int = 1, **kwargs) -> str:
        """Run asynchronously."""
        return self.run(product_name, quantity, **kwargs)
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'AddToCartTool':
        """Create a tool from a dictionary."""
        return cls(**data)
    
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> 'AddToCartTool':
        """Create a tool from a JSON string."""
        return cls.from_dict(json.loads(data))

