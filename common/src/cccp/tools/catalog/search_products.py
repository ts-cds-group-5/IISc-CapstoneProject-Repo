"""Search Products Tool - Searches products by keyword with optional filters."""

from typing import Dict, Any, Optional, List
from cccp.tools.base import BaseCCCPTool
from cccp.core.logging import get_logger
from cccp.core.exceptions import ToolError
from cccp.tools.catalog.catalog_utils import (
    build_filter_where_clauses,
    format_catalog_text,
    format_search_summary
)
from pydantic import BaseModel, Field
import json

logger = get_logger(__name__)


class SearchProductsInput(BaseModel):
    """Input model for SearchProductsTool."""
    keyword: str = Field(..., description="Keyword to search in product names and descriptions")
    collection_name: Optional[str] = Field(None, description="Filter by collection name")
    min_price: Optional[float] = Field(None, description="Minimum price filter")
    max_price: Optional[float] = Field(None, description="Maximum price filter")
    in_stock_only: bool = Field(True, description="Only show products with stock available")


class SearchProductsTool(BaseCCCPTool):
    """Tool for searching products by keyword with optional filters."""
    
    inputs: List[str] = Field(
        default=["keyword", "collection_name", "min_price", "max_price", "in_stock_only"],
        description="Keyword (required) and optional filters"
    )
    outputs: List[str] = Field(default=["search_results"], description="Matching products")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("SearchProductsTool initialized")
    
    def _get_name(self) -> str:
        """Get the tool name."""
        return "searchproducts"
    
    def _get_description(self) -> str:
        """Get the tool description."""
        return "Search products by keyword with optional filters. Use when user asks 'Find laptops', 'Show me products with book', 'Search for Samsung phones', or 'Find items under 10000 in Furniture'"
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate tool inputs."""
        logger.debug(f"SearchProductsTool: Validating inputs - {kwargs}")
        
        # Keyword is required
        keyword = kwargs.get('keyword')
        if not keyword:
            raise ToolError("keyword parameter is required for product search")
        
        if not isinstance(keyword, str):
            raise ToolError(f"keyword must be a string, got: {type(keyword)}")
        
        if len(keyword.strip()) < 2:
            raise ToolError("keyword must be at least 2 characters long")
        
        validated = {
            'keyword': keyword.strip()
        }
        
        # Optional filters
        if collection_name := kwargs.get('collection_name'):
            validated['collection_name'] = str(collection_name)
        
        if min_price := kwargs.get('min_price'):
            try:
                validated['min_price'] = float(min_price)
            except (ValueError, TypeError):
                raise ToolError(f"min_price must be a number, got: {min_price}")
        
        if max_price := kwargs.get('max_price'):
            try:
                validated['max_price'] = float(max_price)
            except (ValueError, TypeError):
                raise ToolError(f"max_price must be a number, got: {max_price}")
        
        # Validate price range
        if 'min_price' in validated and 'max_price' in validated:
            if validated['min_price'] > validated['max_price']:
                raise ToolError(f"min_price ({validated['min_price']}) cannot be greater than max_price ({validated['max_price']})")
        
        # in_stock_only defaults to True
        validated['in_stock_only'] = kwargs.get('in_stock_only', True)
        
        logger.debug(f"SearchProductsTool: Validated inputs - {validated}")
        return validated
    
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool logic."""
        return self._run(**kwargs)
    
    def run(self, keyword: str, collection_name: Optional[str] = None,
            min_price: Optional[float] = None, max_price: Optional[float] = None,
            in_stock_only: bool = True, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            # Validate inputs
            filters = self._validate_inputs(
                keyword=keyword,
                collection_name=collection_name,
                min_price=min_price,
                max_price=max_price,
                in_stock_only=in_stock_only
            )
            
            logger.info(f"SearchProductsTool: Searching for '{keyword}' with filters: {filters}")
            
            # Search products in database
            search_results = self._search_products_in_db(filters)
            
            if not search_results:
                logger.warning(f"SearchProductsTool: No products found for keyword '{keyword}'")
                filter_desc = self._describe_filters(filters)
                return f"No products found matching '{keyword}'{filter_desc}."
            
            logger.info(f"SearchProductsTool: Found {len(search_results)} products")
            
            # Format response with summary
            summary = format_search_summary(search_results, keyword, filters)
            catalog_text = format_catalog_text(search_results)
            response = f"{summary}\n\n{catalog_text}"
            
            logger.debug(f"SearchProductsTool: Formatted response length: {len(response)} chars")
            
            return response
            
        except ToolError as e:
            logger.error(f"SearchProductsTool: Tool error - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"SearchProductsTool: Unexpected error - {str(e)}", exc_info=True)
            raise ToolError(f"Unexpected error: {str(e)}")
    
    def _describe_filters(self, filters: Dict[str, Any]) -> str:
        """Create a human-readable description of applied filters."""
        parts = []
        
        if filters.get('collection_name'):
            parts.append(f"in {filters['collection_name']}")
        
        if filters.get('min_price') or filters.get('max_price'):
            if filters.get('min_price') and filters.get('max_price'):
                parts.append(f"priced between ₹{filters['min_price']:,.2f} and ₹{filters['max_price']:,.2f}")
            elif filters.get('min_price'):
                parts.append(f"priced above ₹{filters['min_price']:,.2f}")
            elif filters.get('max_price'):
                parts.append(f"priced below ₹{filters['max_price']:,.2f}")
        
        if filters.get('in_stock_only'):
            parts.append("in stock")
        
        return " " + " ".join(parts) if parts else ""
    
    def _search_products_in_db(self, filters: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Search products using MCP client with keyword and filters."""
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
                    result = loop.run_until_complete(self._search_products_async(filters))
                    logger.debug(f"SearchProductsTool: Async search completed with {len(result) if result else 0} results")
                except Exception as e:
                    exception = e
                    logger.error(f"SearchProductsTool: Async search failed - {str(e)}")
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
            
            return result
            
        except Exception as e:
            logger.error(f"SearchProductsTool: Database search error - {str(e)}")
            raise ToolError(f"Database error: {str(e)}")
    
    async def _search_products_async(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Async version using MCP client."""
        from cccp.mcp.client import MCPPostgresClient
        
        client = MCPPostgresClient()
        try:
            await client.connect()
            logger.debug("SearchProductsTool: MCP client connected")
            
            # Build search query with keyword and filters
            query, params = self._build_search_query(filters)
            
            logger.debug(f"SearchProductsTool: Executing search query with {len(params)} parameters")
            result = await client.query(query, params)
            logger.info(f"SearchProductsTool: Query returned {len(result)} rows")
            
            return result
            
        except Exception as e:
            logger.error(f"SearchProductsTool: MCP query error - {str(e)}")
            raise
        finally:
            await client.close()
            logger.debug("SearchProductsTool: MCP client closed")
    
    def _build_search_query(self, filters: Dict[str, Any]) -> tuple:
        """Build SQL search query with keyword and dynamic WHERE clauses."""
        # Base query similar to get_catalog but includes keyword search
        base_query = """
            SELECT
                c.collection_id,
                c.name AS collection_name,
                p.product_id,
                p.product_name,
                p.product_description,
                p.currency,
                p.product_price,
                p.product_stock_qty
            FROM public.g5_product p
            JOIN public.collection c
                ON c.collection_id = p.collection_id
        """
        
        # Build WHERE clauses including keyword search
        where_clauses, params = build_filter_where_clauses(filters)
        
        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)
        
        base_query += " ORDER BY c.collection_id, p.product_name"
        
        logger.debug(f"SearchProductsTool: Built search query with {len(where_clauses)} WHERE clauses")
        return base_query, params
    
    def arun(self, keyword: str, collection_name: Optional[str] = None,
             min_price: Optional[float] = None, max_price: Optional[float] = None,
             in_stock_only: bool = True, **kwargs) -> str:
        """Run asynchronously."""
        return self.run(keyword, collection_name, min_price, max_price, in_stock_only, **kwargs)
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchProductsTool':
        """Create a tool from a dictionary."""
        return cls(**data)
    
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> 'SearchProductsTool':
        """Create a tool from a JSON string."""
        return cls.from_dict(json.loads(data))

