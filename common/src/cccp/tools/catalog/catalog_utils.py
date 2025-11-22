"""Utility functions for catalog tools."""

from typing import Dict, Any, List, Tuple, Optional
from cccp.core.logging import get_logger

logger = get_logger(__name__)


def build_filter_where_clauses(filters: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
    """
    Build WHERE clauses and parameters from filter dictionary.
    
    Args:
        filters: Dictionary containing filter values
            - collection_name: str (optional)
            - min_price: float (optional)
            - max_price: float (optional)
            - in_stock_only: bool (default True)
            - keyword: str (optional, for search)
    
    Returns:
        Tuple of (where_clauses list, params dict with numeric string keys in order)
    """
    logger.debug(f"Building filter clauses from: {filters}")
    
    where_clauses = []
    param_values = []  # Keep values in order
    param_index = 1
    
    # Stock filter (default True)
    if filters.get('in_stock_only', True):
        where_clauses.append("p.product_stock_qty > 0")
        logger.debug("Added in_stock filter")
    
    # Collection name filter
    if collection_name := filters.get('collection_name'):
        where_clauses.append(f"c.name = ${param_index}")
        param_values.append(collection_name)
        logger.debug(f"Added collection_name filter: {collection_name} at position {param_index}")
        param_index += 1
    
    # Min price filter
    if min_price := filters.get('min_price'):
        where_clauses.append(f"p.product_price >= ${param_index}")
        param_values.append(float(min_price))
        logger.debug(f"Added min_price filter: {min_price} at position {param_index}")
        param_index += 1
    
    # Max price filter
    if max_price := filters.get('max_price'):
        where_clauses.append(f"p.product_price <= ${param_index}")
        param_values.append(float(max_price))
        logger.debug(f"Added max_price filter: {max_price} at position {param_index}")
        param_index += 1
    
    # Keyword search (for search_products tool)
    if keyword := filters.get('keyword'):
        where_clauses.append(f"(p.product_name ILIKE ${param_index} OR p.product_description ILIKE ${param_index})")
        param_values.append(f"%{keyword}%")
        logger.debug(f"Added keyword filter: {keyword} at position {param_index}")
        param_index += 1
    
    # Convert list to dict with numeric string keys for MCP compatibility
    params = {str(i): val for i, val in enumerate(param_values, 1)}
    
    logger.info(f"Built {len(where_clauses)} WHERE clauses with {len(params)} parameters")
    logger.debug(f"Params dict: {params}")
    return where_clauses, params


def format_price(currency: str, price: float) -> str:
    """
    Format price with currency symbol.
    
    Args:
        currency: Currency code (e.g., 'INR', 'USD')
        price: Price value
    
    Returns:
        Formatted price string (e.g., 'INR 16,999.00')
    """
    try:
        # Currency symbols mapping
        currency_symbols = {
            'INR': '₹',
            'USD': '$',
            'EUR': '€',
            'GBP': '£'
        }
        
        symbol = currency_symbols.get(currency, currency)
        
        # Format with thousands separator and 2 decimal places
        formatted = f"{symbol} {price:,.2f}"
        return formatted
        
    except Exception as e:
        logger.warning(f"Error formatting price: {e}")
        return f"{currency} {price}"


def format_catalog_json(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format catalog results as JSON grouped by collection.
    
    Args:
        results: List of product dictionaries from database
    
    Returns:
        Dictionary with collections and their products
    """
    logger.debug(f"Formatting {len(results)} results as JSON")
    
    try:
        catalog = {}
        
        for row in results:
            collection_id = row.get('collection_id')
            collection_name = row.get('collection_name', 'Unknown')
            
            # Initialize collection if not exists
            if collection_id not in catalog:
                catalog[collection_id] = {
                    'collection_id': collection_id,
                    'collection_name': collection_name,
                    'products': []
                }
            
            # Add product to collection
            product = {
                'product_id': row.get('product_id'),
                'product_name': row.get('product_name'),
                'description': row.get('product_description'),
                'price': float(row.get('product_price', 0)),
                'currency': row.get('currency', 'INR'),
                'stock_qty': row.get('product_stock_qty', 0)
            }
            
            catalog[collection_id]['products'].append(product)
        
        # Convert to list format
        result = {
            'total_collections': len(catalog),
            'total_products': len(results),
            'collections': list(catalog.values())
        }
        
        logger.debug(f"Formatted JSON with {result['total_collections']} collections")
        return result
        
    except Exception as e:
        logger.error(f"Error formatting catalog JSON: {e}")
        return {
            'error': str(e),
            'total_collections': 0,
            'total_products': 0,
            'collections': []
        }


def format_catalog_text(results: List[Dict[str, Any]]) -> str:
    """
    Format catalog results as human-friendly text.
    
    Args:
        results: List of product dictionaries from database
    
    Returns:
        Formatted text string
    """
    logger.debug(f"Formatting {len(results)} results as text")
    
    try:
        if not results:
            return "No products found matching your criteria."
        
        # Group by collection
        collections = {}
        for row in results:
            collection_name = row.get('collection_name', 'Unknown')
            if collection_name not in collections:
                collections[collection_name] = []
            collections[collection_name].append(row)
        
        lines = [f"📋 **Product Catalog** ({len(results)} product{'s' if len(results) != 1 else ''})\n"]
        
        # Format each collection
        for collection_name, products in collections.items():
            lines.append(f"\n📦 **{collection_name}** ({len(products)} product{'s' if len(products) != 1 else ''})")
            lines.append("=" * 60)
            
            for product in products:
                name = product.get('product_name', 'Unknown')
                price = product.get('product_price', 0)
                currency = product.get('currency', 'INR')
                stock = product.get('product_stock_qty', 0)
                description = product.get('product_description', '')
                
                formatted_price = format_price(currency, float(price))
                
                lines.append(f"\n• **{name}**")
                lines.append(f"  Price: {formatted_price}")
                lines.append(f"  Stock: {stock} available")
                if description:
                    # Truncate long descriptions
                    desc_short = description[:100] + "..." if len(description) > 100 else description
                    lines.append(f"  {desc_short}")
        
        formatted = "\n".join(lines)
        logger.debug(f"Formatted text with {len(collections)} collections")
        return formatted
        
    except Exception as e:
        logger.error(f"Error formatting catalog text: {e}")
        return f"Error formatting catalog: {str(e)}"


def validate_collection_exists(collection_name: str, valid_collections: List[str]) -> bool:
    """
    Validate if a collection name exists in the valid collections list.
    
    Args:
        collection_name: Name to validate
        valid_collections: List of valid collection names
    
    Returns:
        True if valid, False otherwise
    """
    # Case-insensitive comparison
    collection_name_lower = collection_name.lower()
    valid_collections_lower = [c.lower() for c in valid_collections]
    
    is_valid = collection_name_lower in valid_collections_lower
    
    if not is_valid:
        logger.warning(f"Invalid collection name: {collection_name}")
    
    return is_valid


def format_search_summary(results: List[Dict[str, Any]], keyword: str, filters: Dict[str, Any]) -> str:
    """
    Format a summary for search results.
    
    Args:
        results: Search results
        keyword: Search keyword used
        filters: Filters applied
    
    Returns:
        Summary string
    """
    try:
        count = len(results)
        
        summary_parts = [f"Found {count} product{'s' if count != 1 else ''} matching '{keyword}'"]
        
        if filters.get('collection_name'):
            summary_parts.append(f"in {filters['collection_name']}")
        
        price_range = []
        if filters.get('min_price'):
            price_range.append(f"from {format_price('INR', filters['min_price'])}")
        if filters.get('max_price'):
            price_range.append(f"up to {format_price('INR', filters['max_price'])}")
        
        if price_range:
            summary_parts.append(" ".join(price_range))
        
        return " ".join(summary_parts) + "."
        
    except Exception as e:
        logger.error(f"Error formatting search summary: {e}")
        return f"Search results for '{keyword}'"

