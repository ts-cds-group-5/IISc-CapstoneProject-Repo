"""tools package for CCCP Advanced."""

# Import catalog tools to ensure they are discovered by the registry
from cccp.tools.catalog.list_collections import ListCollectionsTool
from cccp.tools.catalog.get_catalog import GetCatalogTool
from cccp.tools.catalog.search_products import SearchProductsTool

# Import shopping cart tools
from cccp.tools.order.add_to_cart import AddToCartTool
from cccp.tools.order.remove_from_cart import RemoveFromCartTool
from cccp.tools.order.view_cart import ViewCartTool
from cccp.tools.order.clear_cart import ClearCartTool
from cccp.tools.order.checkout import CheckoutTool

from cccp.tools.registry import (
    tool_registry,
    get_tool,
    get_all_tools,
    register_tool
)

#export these functions
__all__ = [
    "tool_registry",
    "get_tool",
    "get_all_tools",
    "register_tool",
    "ListCollectionsTool",
    "GetCatalogTool",
    "SearchProductsTool",
    "AddToCartTool",
    "RemoveFromCartTool",
    "ViewCartTool",
    "ClearCartTool",
    "CheckoutTool"
]
