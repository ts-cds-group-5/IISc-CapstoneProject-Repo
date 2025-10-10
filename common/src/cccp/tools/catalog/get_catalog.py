"""Get Catalog Tool - Retrieves product catalog with optional filters."""

from typing import Dict, Any, Optional, List
from cccp.tools.base import BaseCCCPTool
from cccp.core.logging import get_logger
from cccp.core.exceptions import ToolError
from cccp.tools.catalog.catalog_utils import (
    build_filter_where_clauses,
    format_catalog_text,
    format_catalog_json
)
from pydantic import BaseModel, Field
import json

logger = get_logger(__name__)


class GetCatalogInput(BaseModel):
    """Input model for GetCatalogTool."""
    collection_name: Optional[str] = Field(None, description="Filter by collection name (e.g., 'Electronics')")
    min_price: Optional[float] = Field(None, description="Minimum price filter")
    max_price: Optional[float] = Field(None, description="Maximum price filter")
    in_stock_only: bool = Field(True, description="Only show products with stock available")


class GetCatalogTool(BaseCCCPTool):
    """Tool for retrieving product catalog with optional filters."""
    
    inputs: List[str] = Field(
        default=["collection_name", "min_price", "max_price", "in_stock_only"],
        description="Optional filters for catalog"
    )
    outputs: List[str] = Field(default=["catalog_data"], description="Product catalog with details")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("GetCatalogTool initialized")
    
    def _get_name(self) -> str:
        """Get the tool name."""
        return "getcatalog"
    
    def _get_description(self) -> str:
        """Get the tool description."""
        return "Get product catalog with optional filters by collection, price range, or stock availability. Use when user asks 'Show me your catalog', 'What products are in Electronics?', or 'Show me products under 5000'"
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate tool inputs."""
        logger.debug(f"GetCatalogTool: Validating inputs - {kwargs}")
        
        validated = {}
        
        # All inputs are optional
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
        
        logger.debug(f"GetCatalogTool: Validated inputs - {validated}")
        return validated
    
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool logic."""
        return self._run(**kwargs)
    
    def run(self, collection_name: Optional[str] = None, min_price: Optional[float] = None,
            max_price: Optional[float] = None, in_stock_only: bool = True, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            # Validate inputs
            filters = self._validate_inputs(
                collection_name=collection_name,
                min_price=min_price,
                max_price=max_price,
                in_stock_only=in_stock_only
            )
            
            logger.info(f"GetCatalogTool: Fetching catalog with filters: {filters}")
            
            # Fetch catalog from database
            catalog_data = self._fetch_catalog_from_db(filters)
            
            if not catalog_data:
                logger.warning("GetCatalogTool: No products found matching filters")
                filter_desc = self._describe_filters(filters)
                return f"No products found{filter_desc}."
            
            logger.info(f"GetCatalogTool: Found {len(catalog_data)} products")
            
            # Format response
            response = format_catalog_text(catalog_data)
            logger.debug(f"GetCatalogTool: Formatted response length: {len(response)} chars")
            
            return response
            
        except ToolError as e:
            logger.error(f"GetCatalogTool: Tool error - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"GetCatalogTool: Unexpected error - {str(e)}", exc_info=True)
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
    
    def _fetch_catalog_from_db(self, filters: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Fetch catalog using MCP client with filters."""
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
                    result = loop.run_until_complete(self._fetch_catalog_async(filters))
                    logger.debug(f"GetCatalogTool: Async fetch completed with {len(result) if result else 0} results")
                except Exception as e:
                    exception = e
                    logger.error(f"GetCatalogTool: Async fetch failed - {str(e)}")
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
            
            return result
            
        except Exception as e:
            logger.error(f"GetCatalogTool: Database fetch error - {str(e)}")
            raise ToolError(f"Database error: {str(e)}")
    
    async def _fetch_catalog_async(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Async version using MCP client."""
        from cccp.mcp.client import MCPPostgresClient
        
        client = MCPPostgresClient()
        try:
            await client.connect()
            logger.debug("GetCatalogTool: MCP client connected")
            
            # Build dynamic query with filters
            query, params = self._build_catalog_query(filters)
            
            logger.debug(f"GetCatalogTool: Executing query with {len(params)} parameters")
            result = await client.query(query, params)
            logger.info(f"GetCatalogTool: Query returned {len(result)} rows")
            
            return result
            
        except Exception as e:
            logger.error(f"GetCatalogTool: MCP query error - {str(e)}")
            raise
        finally:
            await client.close()
            logger.debug("GetCatalogTool: MCP client closed")
    
    def _build_catalog_query(self, filters: Dict[str, Any]) -> tuple:
        """Build SQL query with dynamic WHERE clauses based on filters."""
        # Base query from README-docker.md lines 258-271
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
        
        # Build WHERE clauses using utility function
        where_clauses, params = build_filter_where_clauses(filters)
        
        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)
        
        base_query += " ORDER BY c.collection_id, p.product_name"
        
        logger.debug(f"GetCatalogTool: Built query with {len(where_clauses)} WHERE clauses")
        return base_query, params
    
    def arun(self, collection_name: Optional[str] = None, min_price: Optional[float] = None,
             max_price: Optional[float] = None, in_stock_only: bool = True, **kwargs) -> str:
        """Run asynchronously."""
        return self.run(collection_name, min_price, max_price, in_stock_only, **kwargs)
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'GetCatalogTool':
        """Create a tool from a dictionary."""
        return cls(**data)
    
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> 'GetCatalogTool':
        """Create a tool from a JSON string."""
        return cls.from_dict(json.loads(data))

