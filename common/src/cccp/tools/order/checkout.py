"""Checkout Tool - Complete order placement with shipping details."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from cccp.tools.base import BaseCCCPTool
from cccp.core.logging import get_logger
from cccp.core.exceptions import ToolError
from cccp.tools.order.cart_utils import (
    validate_cart,
    get_or_create_cart
)
from pydantic import BaseModel, Field
import json

logger = get_logger(__name__)


class CheckoutInput(BaseModel):
    """Input model for CheckoutTool."""
    shipping_address: Optional[str] = Field(None, description="Shipping address for delivery")
    shipping_notes: Optional[str] = Field(None, description="Special delivery instructions")


class CheckoutTool(BaseCCCPTool):
    """Tool for completing order checkout and placement."""
    
    inputs: List[str] = Field(
        default=["shipping_address", "shipping_notes"],
        description="Shipping details (address required, notes optional)"
    )
    outputs: List[str] = Field(default=["order_confirmation"], description="Order confirmation with full details")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("CheckoutTool initialized")
    
    def _get_name(self) -> str:
        """Get the tool name."""
        return "checkout"
    
    def _get_description(self) -> str:
        """Get the tool description."""
        return "Complete order and checkout. Use when user says 'checkout', 'place order', 'complete order', 'buy now', 'finish order'"
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate tool inputs."""
        logger.debug(f"CheckoutTool: Validating inputs - {kwargs}")
        
        validated = {}
        
        if shipping_address := kwargs.get('shipping_address'):
            if isinstance(shipping_address, str) and len(shipping_address.strip()) >= 10:
                validated['shipping_address'] = shipping_address.strip()
            else:
                raise ToolError("shipping_address must be at least 10 characters")
        
        if shipping_notes := kwargs.get('shipping_notes'):
            validated['shipping_notes'] = str(shipping_notes).strip()
        
        return validated
    
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool logic."""
        return self._run(**kwargs)
    
    def run(self, shipping_address: Optional[str] = None, shipping_notes: Optional[str] = None, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            logger.info("CheckoutTool: Starting checkout process")
            
            # Get user session from kwargs
            user_session = kwargs.get('user_session')
            
            # Get cart from session
            cart = self._get_cart_from_session(user_session)
            
            # Validate cart
            validate_cart(cart)
            
            # Get customer info from session
            customer_info = self._get_customer_info(user_session)
            
            # Handle shipping address
            if not shipping_address:
                # Ask for shipping address
                logger.info("CheckoutTool: No shipping address provided, requesting from user")
                return self._request_shipping_address(cart)
            
            # Validate shipping address
            validated = self._validate_inputs(
                shipping_address=shipping_address,
                shipping_notes=shipping_notes
            )
            
            logger.info(f"CheckoutTool: Placing order for {customer_info['name']}")
            
            # Create order in database
            order_id = self._create_order_in_db(
                cart=cart,
                customer=customer_info,
                shipping_address=validated['shipping_address'],
                shipping_notes=validated.get('shipping_notes', '')
            )
            
            logger.info(f"CheckoutTool: Order created successfully - Order ID: {order_id}")
            
            # Clear cart from session
            self._clear_cart_from_session(user_session)
            
            # Format comprehensive order confirmation
            response = self._format_order_confirmation(
                order_id=order_id,
                cart=cart,
                customer=customer_info,
                shipping_address=validated['shipping_address'],
                shipping_notes=validated.get('shipping_notes', '')
            )
            
            logger.info(f"CheckoutTool: Checkout complete for Order ID: {order_id}")
            return response
            
        except ToolError as e:
            logger.error(f"CheckoutTool: Tool error - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"CheckoutTool: Unexpected error - {str(e)}", exc_info=True)
            raise ToolError(f"Unexpected error: {str(e)}")
    
    def _request_shipping_address(self, cart: Dict[str, Any]) -> str:
        """Request shipping address from user."""
        lines = [
            "📋 Ready to place your order!\n",
            f"Cart Total: ₹{cart['grand_total']:,.2f} for {cart['total_items']} product{'s' if cart['total_items'] != 1 else ''}\n",
            "Please provide your shipping address to complete the order.",
            "\nExample: '123 Main Street, Bangalore, Karnataka 560001'"
        ]
        return "\n".join(lines)
    
    def _get_customer_info(self) -> Dict[str, str]:
        """Get customer information from session."""
        if not self.agent or not hasattr(self.agent, 'user_session') or not self.agent.user_session:
            raise ToolError("Customer information not available. Please register first.")
        
        session = self.agent.user_session
        
        if not all(key in session for key in ['name', 'email']):
            raise ToolError("Customer information incomplete. Please provide your name and email.")
        
        customer_info = {
            'name': session.get('name', ''),
            'email': session.get('email', ''),
            'mobile': session.get('mobile', 'Not provided')
        }
        
        logger.debug(f"CheckoutTool: Customer info retrieved for {customer_info['name']}")
        return customer_info
    
    def _create_order_in_db(self, cart: Dict, customer: Dict, 
                           shipping_address: str, shipping_notes: str) -> int:
        """Create order and order items in database."""
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
                    result = loop.run_until_complete(
                        self._create_order_async(cart, customer, shipping_address, shipping_notes)
                    )
                    logger.debug(f"CheckoutTool: Order creation completed - Order ID: {result}")
                except Exception as e:
                    exception = e
                    logger.error(f"CheckoutTool: Order creation failed - {str(e)}")
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
            
            return result
            
        except Exception as e:
            logger.error(f"CheckoutTool: Database error - {str(e)}")
            raise ToolError(f"Failed to create order: {str(e)}")
    
    async def _create_order_async(self, cart: Dict, customer: Dict,
                                   shipping_address: str, shipping_notes: str) -> int:
        """Async order creation with transaction."""
        from cccp.mcp.client import MCPPostgresClient
        
        client = MCPPostgresClient()
        try:
            await client.connect()
            logger.debug("CheckoutTool: MCP client connected")
            
            # 1. Create order record
            order_query = """
                INSERT INTO g5_order (
                    customer_name, customer_email, customer_phone,
                    shipping_address, shipping_notes,
                    currency, payment_mode, order_status, total_price
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9
                ) RETURNING order_id
            """
            
            order_params = {
                '1': customer['name'],
                '2': customer['email'],
                '3': customer['mobile'],
                '4': shipping_address,
                '5': shipping_notes if shipping_notes else '',
                '6': cart['currency'],
                '7': 'COD',
                '8': 'received',
                '9': float(cart['grand_total'])
            }
            
            logger.debug(f"CheckoutTool: Creating order with params: {order_params}")
            order_result = await client.query(order_query, order_params)
            
            if not order_result or not order_result[0].get('order_id'):
                raise Exception("Failed to create order - no order_id returned")
            
            order_id = order_result[0]['order_id']
            logger.info(f"CheckoutTool: Order created - ID: {order_id}")
            
            # 2. Create order items for each cart item
            for item in cart['items']:
                item_query = """
                    INSERT INTO g5_order_items (
                        order_id, product_id, product_name,
                        currency, unit_price, quantity
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6
                    )
                """
                
                item_params = {
                    '1': order_id,
                    '2': item['product_id'],
                    '3': item['product_name'],
                    '4': item['currency'],
                    '5': float(item['unit_price']),
                    '6': item['quantity']
                }
                
                logger.debug(f"CheckoutTool: Creating order item for product {item['product_id']}")
                await client.query(item_query, item_params)
                logger.debug(f"CheckoutTool: Order item created for {item['product_name']}")
            
            logger.info(f"CheckoutTool: All {len(cart['items'])} order items created")
            return order_id
            
        except Exception as e:
            logger.error(f"CheckoutTool: Database transaction error - {str(e)}")
            raise
        finally:
            await client.close()
            logger.debug("CheckoutTool: MCP client closed")
    
    def _format_order_confirmation(self, order_id: int, cart: Dict, customer: Dict,
                                   shipping_address: str, shipping_notes: str) -> str:
        """Format comprehensive order confirmation with ALL details."""
        
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        lines = [
            "✅ Order Placed Successfully!\n",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "ORDER CONFIRMATION",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
            f"Order ID: #{order_id}",
            f"Order Status: Received",
            f"Payment Mode: COD (Cash on Delivery)",
            f"Order Date: {order_date}\n",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "CUSTOMER INFORMATION",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
            f"Name: {customer['name']}",
            f"Email: {customer['email']}",
            f"Phone: {customer['mobile']}\n",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "ORDER ITEMS",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        ]
        
        # Add all order items with full details
        for i, item in enumerate(cart['items'], 1):
            lines.append(f"{i}. {item['product_name']}")
            
            # Show description if available
            if item.get('product_description'):
                lines.append(f"   {item['product_description'][:100]}")
            
            lines.append(f"   Quantity: {item['quantity']}")
            lines.append(f"   Unit Price: ₹{item['unit_price']:,.2f}")
            lines.append(f"   Line Total: ₹{item['line_total']:,.2f}\n")
        
        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "SHIPPING DETAILS",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
            "Shipping Address:",
            shipping_address
        ])
        
        if shipping_notes:
            lines.append(f"\nShipping Notes:")
            lines.append(shipping_notes)
        
        lines.extend([
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "ORDER SUMMARY",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
            f"Total Items: {cart['total_items']} product{'s' if cart['total_items'] != 1 else ''}",
            f"Total Quantity: {cart['total_quantity']} unit{'s' if cart['total_quantity'] != 1 else ''}",
            f"Grand Total: ₹{cart['grand_total']:,.2f}\n",
            "Your order will be processed shortly.",
            "Thank you for shopping with us! 🎉"
        ])
        
        return "\n".join(lines)
    
    def _get_cart_from_session(self) -> Dict[str, Any]:
        """Get cart from user session via agent."""
        if not self.agent or not hasattr(self.agent, 'user_session'):
            logger.warning("CheckoutTool: No agent or session available")
            return get_or_create_cart()
        
        if not self.agent.user_session:
            logger.warning("CheckoutTool: No user session")
            return get_or_create_cart()
        
        cart = self.agent.user_session.get('shopping_cart')
        if not cart:
            logger.info("CheckoutTool: No cart in session")
            cart = get_or_create_cart()
        
        return cart
    
    def _get_customer_info(self, user_session: Optional[Dict]) -> Dict[str, str]:
        """Get customer information from session."""
        if not user_session:
            raise ToolError("Customer information not available. Please register first with your name, email, and mobile number.")
        
        if not all(key in user_session for key in ['name', 'email']):
            raise ToolError("Customer information incomplete. Please provide your name and email.")
        
        customer_info = {
            'name': user_session.get('name', ''),
            'email': user_session.get('email', ''),
            'mobile': user_session.get('mobile', 'Not provided')
        }
        
        logger.debug(f"CheckoutTool: Customer info retrieved for {customer_info['name']}")
        return customer_info
    
    def _get_cart_from_session(self, user_session: Optional[Dict]) -> Dict[str, Any]:
        """Get cart from user session."""
        if not user_session:
            logger.warning("CheckoutTool: No user session available")
            return get_or_create_cart()
        
        cart = user_session.get('shopping_cart')
        if not cart:
            logger.info("CheckoutTool: No cart in session")
            cart = get_or_create_cart()
        
        return cart
    
    def _clear_cart_from_session(self, user_session: Optional[Dict]) -> None:
        """Clear cart from user session after successful order."""
        if user_session and 'shopping_cart' in user_session:
            del user_session['shopping_cart']
            logger.debug("CheckoutTool: Cart cleared from session after order placement")
    
    def arun(self, shipping_address: Optional[str] = None, 
             shipping_notes: Optional[str] = None, **kwargs) -> str:
        """Run asynchronously."""
        return self.run(shipping_address, shipping_notes, **kwargs)
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckoutTool':
        """Create a tool from a dictionary."""
        return cls(**data)
    
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> 'CheckoutTool':
        """Create a tool from a JSON string."""
        return cls.from_dict(json.loads(data))

