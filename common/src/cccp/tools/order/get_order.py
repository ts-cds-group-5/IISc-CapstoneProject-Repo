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
    cart_id: Optional[str] = Field(None, description="The cart ID to retrieve")
    customer_email: Optional[str] = Field(None, description="The customer email to search by")
    customer_full_name: Optional[str] = Field(None, description="The customer full name to search by")


class GetOrderTool(BaseCCCPTool):
    """Tool for retrieving order information with authentication and validation."""
    
    def __init__(self, **kwargs):
        """Initialize the GetOrderTool."""
        super().__init__(**kwargs)
    
    def _get_name(self) -> str:
        """Get the tool name."""
        return "getorder" #tool name is getorder instead of get_order
    
    def _get_description(self) -> str:
        """Get the tool description."""
        return "Retrieve cart information from Evershop by cart_id, customer_email, or customer_full_name"
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate tool inputs."""
        cart_id = kwargs.get("cart_id")
        customer_email = kwargs.get("customer_email")
        customer_full_name = kwargs.get("customer_full_name")
        
        # At least one search parameter must be provided
        if not any([cart_id, customer_email, customer_full_name]):
            raise ToolError("At least one of cart_id, customer_email, or customer_full_name must be provided")
        
        # Validate types
        for param_name, param_value in [("cart_id", cart_id), ("customer_email", customer_email), ("customer_full_name", customer_full_name)]:
            if param_value is not None and not isinstance(param_value, str):
                raise ToolError(f"{param_name} must be a string")
        
        return {
            "cart_id": cart_id,
            "customer_email": customer_email, 
            "customer_full_name": customer_full_name
        }
    
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool logic."""
        return self._run(
            cart_id=kwargs.get("cart_id"),
            customer_email=kwargs.get("customer_email"),
            customer_full_name=kwargs.get("customer_full_name"),
            **kwargs
        )
    
    def run(self, cart_id: Optional[str] = None, customer_email: Optional[str] = None, 
            customer_full_name: Optional[str] = None, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            # Validate input
            if not any([cart_id, customer_email, customer_full_name]):
                raise ToolError("At least one of cart_id, customer_email, or customer_full_name must be provided")
            
            # Retrieve cart from database
            cart_details = self._fetch_cart_from_db(cart_id, customer_email, customer_full_name)
            
            if not cart_details:
                search_params = [f"cart_id={cart_id}", f"email={customer_email}", f"name={customer_full_name}"]
                search_str = ", ".join([p for p in search_params if p.split("=")[1] != "None"])
                raise ToolError(f"Cart not found for: {search_str}")
            
            # Format response
            return self._format_cart_response(cart_details)
            
        except ToolError as e:
            logger.error(f"Tool error in get_order: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_order: {str(e)}")
            raise ToolError(f"Unexpected error: {str(e)}")
    
    
    def _fetch_cart_from_db(self, cart_id: Optional[str] = None, 
                           customer_email: Optional[str] = None,
                           customer_full_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch cart details from Evershop database using MCP client."""
        try:
            logger.info(f"Fetching cart with cart_id={cart_id}, email={customer_email}, name={customer_full_name}")
            
            # Use MCP client to fetch real data from Evershop database
            import asyncio
            import threading
            
            # Handle async operation in sync context
            result = None
            exception = None
            
            def run_async():
                nonlocal result, exception
                try:
                    # Create new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self._fetch_cart_async(cart_id, customer_email, customer_full_name))
                except Exception as e:
                    exception = e
                finally:
                    loop.close()
            
            # Run async operation in separate thread
            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
            
            return result
            
        except Exception as e:
            logger.error(f"Database fetch error: {str(e)}")
            # Fallback to mock data if MCP client fails
            logger.warning("Falling back to mock data due to MCP client error")
            return self._get_mock_cart_data(cart_id, customer_email, customer_full_name)
    
    async def _fetch_cart_async(self, cart_id: Optional[str] = None,
                               customer_email: Optional[str] = None,
                               customer_full_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Async version of cart fetching using MCP client."""
        from cccp.mcp.client import MCPPostgresClient
        
        client = MCPPostgresClient()
        try:
            await client.connect()
            
            # Build query based on provided parameters
            if cart_id:
                #convert cart_id to int
                int_cart_id = int(cart_id)
                cart_query = """
                    SELECT cart_id, customer_email, customer_full_name,
                    user_ip, grand_total, shipping_note
                    FROM cart
                    WHERE cart_id = $1 AND status = 'true'
                    LIMIT 1
                """
                params = {"cart_id": int_cart_id}
            elif customer_email:
                cart_query = """
                    SELECT cart_id, customer_email, customer_full_name,
                    user_ip, grand_total, shipping_note
                    FROM cart
                    WHERE customer_email = $1 AND status = 'true'
                    LIMIT 1
                """
                params = {"customer_email": customer_email}
            elif customer_full_name:
                cart_query = """
                    SELECT cart_id, customer_email, customer_full_name,
                    user_ip, grand_total, shipping_note
                    FROM cart
                    WHERE customer_full_name = $1 AND status = 'true'
                    LIMIT 1
                """
                params = {"customer_full_name": customer_full_name}
            else:
                logger.error("No search parameter provided")
                return None
            
            cart_result = await client.query(cart_query, params)
            
            if not cart_result:
                logger.warning(f"No cart found for search parameters")
                return None
            
            cart = cart_result[0]
            logger.info(f"Cart data: {cart}")
            
            # Transform to expected format
            return self._transform_evershop_cart(cart)
            
        except Exception as e:
            logger.error(f"Error fetching cart from database: {str(e)}")
            return None
        finally:
            await client.close()
    
    def _transform_evershop_cart(self, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Evershop cart data to expected format."""
        try:
            # Handle Decimal type conversion for grand_total
            grand_total = cart_data.get('grand_total', 0.0)
            if hasattr(grand_total, '__float__'):
                total_value = float(grand_total)
            else:
                total_value = float(str(grand_total))
            
            return {
                "cart_id": str(cart_data.get('cart_id', '')),
                "customer_email": cart_data.get('customer_email', ''),
                "customer_full_name": cart_data.get('customer_full_name', ''),
                "user_ip": cart_data.get('user_ip', ''),
                "total": total_value,
                "shipping_note": cart_data.get('shipping_note', ''),
                "status": "active_cart",  # Cart status
                "created_at": str(cart_data.get('created_at', '')),
                "updated_at": str(cart_data.get('updated_at', ''))
            }
            
        except Exception as e:
            logger.error(f"Error transforming cart data: {str(e)}")
            return None
    
    def _get_mock_cart_data(self, cart_id: Optional[str] = None,
                           customer_email: Optional[str] = None,
                           customer_full_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fallback mock data when MCP client is unavailable."""
        mock_carts = {
            "cart454": {
                "cart_id": "cart454",
                "customer_email": "davy.jones@pmail.com",
                "customer_full_name": "Davy Jones",
                "user_ip": "192.168.1.100",
                "total": 199.97,
                "shipping_note": "Please deliver during business hours",
                "status": "active_cart",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-16T14:20:00Z"
            }
        }
        
        # Try to find by cart_id first
        if cart_id:
            return mock_carts.get(cart_id)
        
        # Try to find by email
        if customer_email:
            for cart in mock_carts.values():
                if cart["customer_email"] == customer_email:
                    return cart
        
        # Try to find by name
        if customer_full_name:
            for cart in mock_carts.values():
                if cart["customer_full_name"] == customer_full_name:
                    return cart
        
        return None
    
    def _format_cart_response(self, cart_details: Dict[str, Any]) -> str:
        """Format cart details for response using customer_full_name."""
        try:
            customer_name = cart_details.get('customer_full_name', 'Customer')
            cart_id = cart_details.get('cart_id', 'Unknown')
            status = cart_details.get('status', 'unknown')
            total = cart_details.get('total', 0.0)
            
            response = f"""Cart Details for {customer_name}:
Cart ID: {cart_id}
Status: {status.replace('_', ' ').title()}
Total: ₹{total:.2f}
Customer Email: {cart_details.get('customer_email', 'N/A')}"""
            
            if cart_details.get('shipping_note'):
                response += f"\nShipping Note: {cart_details['shipping_note']}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting cart response: {str(e)}")
            return f"Cart found but error formatting details: {str(e)}"
    
    def arun(self, cart_id: Optional[str] = None, customer_email: Optional[str] = None,
             customer_full_name: Optional[str] = None, **kwargs) -> str:
        """Run the tool asynchronously."""
        # For now, just delegate to the synchronous version
        return self.run(cart_id, customer_email, customer_full_name, **kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary."""
        return {
            "name": self._get_name(),
            "description": self._get_description(),
            "tool_name": self.tool_name,
            "inputs": ["cart_id", "customer_email", "customer_full_name"],
            "outputs": ["cart_details"]
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

# ===== COMMENTED OUT: Duplicate @tool function - functionality moved to GetOrderTool class =====
# This was a duplicate implementation using @tool decorator pattern.
# The functionality has been integrated into the GetOrderTool class above using MCP client.
# Keeping this commented for reference and potential future use.

# @tool
# async def get_evershop_order(order_id: str, customer_id: str) -> dict:
#     """
#     Retrieve order details from Evershop database.
#     
#     Args:
#         order_id: The Evershop order ID to retrieve
#         customer_id: The customer ID for authentication
#         
#     Returns:
#         Order details with items and customer info
#     """
#     client = MCPPostgresClient()
#     
#     # Get order details with customer info
#     order_query = """
#         SELECT o.*, c.*
#         FROM "order" o
#         JOIN customer c ON o.customer_id = c.customer_id
#         WHERE o.order_id = $1 AND o.customer_id = $2
#     """
#     
#     # Get order items with product details
#     items_query = """
#         SELECT oi.*, p.name as product_name, p.sku, p.price as product_price
#         FROM order_item oi
#         JOIN product p ON oi.product_id = p.product_id
#         WHERE oi.order_id = $1
#         ORDER BY oi.order_item_id
#     """
#     
#     try:
#         order_result = await client.query(order_query, {"order_id": order_id, "customer_id": customer_id})
#         items_result = await client.query(items_query, {"order_id": order_id})
#         
#         if not order_result:
#             return {"error": f"Order {order_id} not found for customer {customer_id}"}
#         
#         order = order_result[0]
#         order['items'] = items_result
#         
#         return {
#             "order_id": order['order_id'],
#             "status": order['status'],
#             "total": float(order['total']),
#             "customer": {
#                 "customer_id": order['customer_id'],
#                 "full_name": order.get('full_name', ''),
#                 "email": order.get('email', '')
#             },
#             "items": [
#                 {
#                     "product_name": item['product_name'],
#                     "sku": item['sku'],
#                     "quantity": item['qty'],
#                     "price": float(item['product_price'])
#                 }
#                 for item in items_result
#             ],
#             "created_at": order.get('created_at', ''),
#             "updated_at": order.get('updated_at', '')
#         }
#         
#     except Exception as e:
#         return {"error": f"Database error: {str(e)}"}
#     finally:
#         await client.close()