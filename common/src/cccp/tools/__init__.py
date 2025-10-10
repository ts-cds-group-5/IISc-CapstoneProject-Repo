"""tools package for CCCP Advanced."""

# Import catalog tools to ensure they are discovered by the registry
from cccp.tools.catalog.list_collections import ListCollectionsTool
from cccp.tools.catalog.get_catalog import GetCatalogTool
from cccp.tools.catalog.search_products import SearchProductsTool

# Import place order stub
from cccp.tools.order.place_order import PlaceOrderTool

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
    "PlaceOrderTool"
]
