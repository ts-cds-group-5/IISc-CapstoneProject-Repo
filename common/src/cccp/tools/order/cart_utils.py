"""Shopping cart utility functions for order management."""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from cccp.core.logging import get_logger
from cccp.core.config import get_settings

logger = get_logger(__name__)


def get_or_create_cart() -> Dict[str, Any]:
    """
    Get or create an empty shopping cart.
    
    Returns:
        Empty cart dictionary structure
    """
    logger.debug("Creating new empty cart")
    return {
        'items': [],
        'total_items': 0,
        'total_quantity': 0,
        'grand_total': 0.0,
        'currency': 'INR',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }


def add_item_to_cart(cart: Dict[str, Any], product: Dict[str, Any], quantity: int) -> Tuple[Dict[str, Any], str]:
    """
    Add a product to the shopping cart.
    
    Args:
        cart: Current cart state
        product: Product dict with id, name, price, description, stock
        quantity: Quantity to add
    
    Returns:
        Tuple of (updated cart, status message)
    
    Raises:
        ValueError: If validation fails
    """
    settings = get_settings()
    max_items = getattr(settings, 'cart_max_items', 10)
    
    # Validation
    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0")
    
    if cart['total_items'] >= max_items:
        raise ValueError(f"Cart is full (max {max_items} items). Remove items or checkout.")
    
    # Check if product already in cart
    for item in cart['items']:
        if item['product_id'] == product['product_id']:
            raise ValueError(f"{product['product_name']} is already in your cart. Use 'remove' then 'add' to change quantity.")
    
    # Check stock availability
    if product.get('product_stock_qty', 0) < quantity:
        raise ValueError(f"Insufficient stock. Only {product.get('product_stock_qty', 0)} units available.")
    
    # Create cart item
    line_total = float(product['product_price']) * quantity
    cart_item = {
        'product_id': product['product_id'],
        'product_name': product['product_name'],
        'product_description': product.get('product_description', ''),
        'unit_price': float(product['product_price']),
        'currency': product.get('currency', 'INR'),
        'quantity': quantity,
        'line_total': line_total
    }
    
    # Add to cart
    cart['items'].append(cart_item)
    cart['updated_at'] = datetime.now().isoformat()
    
    # Recalculate totals
    cart = calculate_totals(cart)
    
    logger.info(f"Added to cart: {product['product_name']} × {quantity}")
    
    message = f"✅ Added to cart: {product['product_name']} (₹{product['product_price']:,.2f} × {quantity})"
    return cart, message


def remove_item_from_cart(cart: Dict[str, Any], product_name: str) -> Tuple[Dict[str, Any], str]:
    """
    Remove a product from the shopping cart.
    
    Args:
        cart: Current cart state
        product_name: Product name to remove (fuzzy match)
    
    Returns:
        Tuple of (updated cart, status message)
    
    Raises:
        ValueError: If product not found in cart
    """
    if not cart or not cart.get('items'):
        raise ValueError("Your cart is empty.")
    
    # Find product in cart (case-insensitive partial match)
    product_name_lower = product_name.lower()
    removed_item = None
    
    for i, item in enumerate(cart['items']):
        if product_name_lower in item['product_name'].lower():
            removed_item = cart['items'].pop(i)
            break
    
    if not removed_item:
        raise ValueError(f"Product '{product_name}' not found in your cart.")
    
    # Update timestamp
    cart['updated_at'] = datetime.now().isoformat()
    
    # Recalculate totals
    cart = calculate_totals(cart)
    
    logger.info(f"Removed from cart: {removed_item['product_name']}")
    
    message = f"✅ Removed: {removed_item['product_name']}"
    return cart, message


def calculate_totals(cart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate cart totals.
    
    Args:
        cart: Cart dictionary
    
    Returns:
        Cart with updated totals
    """
    cart['total_items'] = len(cart['items'])
    cart['total_quantity'] = sum(item['quantity'] for item in cart['items'])
    cart['grand_total'] = sum(item['line_total'] for item in cart['items'])
    
    logger.debug(f"Cart totals: {cart['total_items']} items, {cart['total_quantity']} units, ₹{cart['grand_total']:,.2f}")
    
    return cart


def validate_cart(cart: Dict[str, Any]) -> bool:
    """
    Validate cart is ready for checkout.
    
    Args:
        cart: Cart dictionary
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If validation fails
    """
    if not cart or not cart.get('items'):
        raise ValueError("Your cart is empty. Add items before checking out.")
    
    if cart['total_items'] == 0:
        raise ValueError("Your cart is empty. Add items before checking out.")
    
    if cart['grand_total'] <= 0:
        raise ValueError("Invalid cart total.")
    
    logger.debug(f"Cart validation passed: {cart['total_items']} items")
    return True


def format_cart_display(cart: Dict[str, Any]) -> str:
    """
    Format cart contents for display.
    
    Args:
        cart: Cart dictionary
    
    Returns:
        Formatted cart string
    """
    if not cart or not cart.get('items'):
        return "🛒 Your shopping cart is empty.\n\nBrowse our catalog and add items to get started!"
    
    lines = ["🛒 Your Shopping Cart:\n"]
    
    for i, item in enumerate(cart['items'], 1):
        lines.append(f"{i}. {item['product_name']} × {item['quantity']}")
        
        # Show description (truncated)
        if item.get('product_description'):
            desc = item['product_description'][:80]
            if len(item['product_description']) > 80:
                desc += "..."
            lines.append(f"   {desc}")
        
        lines.append(f"   Unit Price: ₹{item['unit_price']:,.2f}")
        lines.append(f"   Subtotal: ₹{item['line_total']:,.2f}\n")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"Total Items: {cart['total_items']} product{'s' if cart['total_items'] != 1 else ''} ({cart['total_quantity']} unit{'s' if cart['total_quantity'] != 1 else ''})")
    lines.append(f"Grand Total: ₹{cart['grand_total']:,.2f}")
    lines.append("Payment: COD (Cash on Delivery)")
    lines.append("\nReady to checkout? Say 'checkout' or 'place order'.")
    
    return "\n".join(lines)


def format_cart_summary(cart: Dict[str, Any]) -> str:
    """
    Format brief cart summary (for add/remove operations).
    
    Args:
        cart: Cart dictionary
    
    Returns:
        Brief summary string
    """
    if not cart or not cart.get('items'):
        return "Cart: 0 items"
    
    return f"Cart: {cart['total_items']} item{'s' if cart['total_items'] != 1 else ''}, Total: ₹{cart['grand_total']:,.2f}"


def find_product_in_cart(cart: Dict[str, Any], product_name: str) -> Optional[Dict[str, Any]]:
    """
    Find a product in cart by name (fuzzy match).
    
    Args:
        cart: Cart dictionary
        product_name: Product name to search for
    
    Returns:
        Product dict if found, None otherwise
    """
    product_name_lower = product_name.lower()
    
    for item in cart.get('items', []):
        if product_name_lower in item['product_name'].lower():
            return item
    
    return None


def get_cart_item_count(cart: Dict[str, Any]) -> int:
    """
    Get number of distinct items in cart.
    
    Args:
        cart: Cart dictionary
    
    Returns:
        Number of distinct items
    """
    return cart.get('total_items', 0) if cart else 0


def is_cart_empty(cart: Dict[str, Any]) -> bool:
    """
    Check if cart is empty.
    
    Args:
        cart: Cart dictionary
    
    Returns:
        True if cart is empty
    """
    return not cart or not cart.get('items') or cart.get('total_items', 0) == 0

