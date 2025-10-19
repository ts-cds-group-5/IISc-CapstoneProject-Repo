"""List Collections Tool - Lists all product collections with counts."""

from typing import Dict, Any, Optional, List
from cccp.tools.base import BaseCCCPTool
from cccp.core.logging import get_logger
from cccp.core.exceptions import ToolError
from pydantic import BaseModel, Field
import json

logger = get_logger(__name__)


class ListCollectionsInput(BaseModel):
    """Input model for ListCollectionsTool (no parameters required)."""
    pass


class ListCollectionsTool(BaseCCCPTool):
    """Tool for listing all product collections with product counts."""
    
    inputs: List[str] = Field(default=[], description="No input parameters required")
    outputs: List[str] = Field(default=["collections_list"], description="List of collections with counts")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("ListCollectionsTool initialized")
    
    def _get_name(self) -> str:
        """Get the tool name."""
        return "listcollections"
    
    def _get_description(self) -> str:
        """Get the tool description."""
        return "List all product collections with product counts. Use this when user asks 'What collections do you have?', 'What items are available?', or 'Show me your collections'"
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """No inputs to validate."""
        logger.debug("ListCollectionsTool: No inputs to validate")
        return {}
    
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool logic."""
        return self._run(**kwargs)
    
    def run(self, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            logger.info("ListCollectionsTool: Fetching collections from database")
            
            # Fetch collections from database
            collections_data = self._fetch_collections_from_db()
            
            if not collections_data:
                logger.warning("ListCollectionsTool: No collections found in database")
                return "No collections found in the catalog."
            
            logger.info(f"ListCollectionsTool: Found {len(collections_data)} collections")
            
            # Format response
            response = self._format_collections_response(collections_data)
            logger.debug(f"ListCollectionsTool: Formatted response length: {len(response)} chars")
            
            return response
            
        except ToolError as e:
            logger.error(f"ListCollectionsTool: Tool error - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"ListCollectionsTool: Unexpected error - {str(e)}", exc_info=True)
            raise ToolError(f"Unexpected error: {str(e)}")
    
    def _fetch_collections_from_db(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch collections using MCP client."""
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
                    result = loop.run_until_complete(self._fetch_collections_async())
                    logger.debug(f"ListCollectionsTool: Async fetch completed with {len(result) if result else 0} results")
                except Exception as e:
                    exception = e
                    logger.error(f"ListCollectionsTool: Async fetch failed - {str(e)}")
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
            
            return result
            
        except Exception as e:
            logger.error(f"ListCollectionsTool: Database fetch error - {str(e)}")
            raise ToolError(f"Database error: {str(e)}")
    
    async def _fetch_collections_async(self) -> List[Dict[str, Any]]:
        """Async version using MCP client."""
        from cccp.mcp.client import MCPPostgresClient
        
        client = MCPPostgresClient()
        try:
            await client.connect()
            logger.debug("ListCollectionsTool: MCP client connected")
            
            # SQL from README-docker.md lines 218-229
            query = """
                SELECT
                    c.collection_id,
                    c.name AS collection_name,
                    c.code AS collection_code,
                    COUNT(p.product_id) AS product_count
                FROM public.collection c
                LEFT JOIN public.g5_product p
                    ON p.collection_id = c.collection_id
                GROUP BY c.collection_id, c.name, c.code
                ORDER BY c.collection_id
            """
            
            logger.debug("ListCollectionsTool: Executing query")
            result = await client.query(query, {})
            logger.info(f"ListCollectionsTool: Query returned {len(result)} rows")
            
            return result
            
        except Exception as e:
            logger.error(f"ListCollectionsTool: MCP query error - {str(e)}")
            raise
        finally:
            await client.close()
            logger.debug("ListCollectionsTool: MCP client closed")
    
    def _format_collections_response(self, collections_data: List[Dict[str, Any]]) -> str:
        """Format collections for human-friendly response."""
        try:
            lines = ["🛍️  **Available Collections:**\n"]
            total_products = 0
            
            for collection in collections_data:
                name = collection.get('collection_name', 'Unknown')
                count = collection.get('product_count', 0)
                code = collection.get('collection_code', '')
                
                lines.append(f"📦 **{name}** ({code})")
                lines.append(f"   └─ {count} product{'s' if count != 1 else ''}")
                total_products += count
            
            lines.append(f"\n✨ Total: {len(collections_data)} collections with {total_products} products")
            
            formatted = "\n".join(lines)
            logger.debug(f"ListCollectionsTool: Formatted {len(collections_data)} collections")
            return formatted
            
        except Exception as e:
            logger.error(f"ListCollectionsTool: Formatting error - {str(e)}")
            return f"Collections found but error formatting: {str(e)}"
    
    def arun(self, **kwargs) -> str:
        """Run asynchronously."""
        return self.run(**kwargs)
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'ListCollectionsTool':
        """Create a tool from a dictionary."""
        return cls(**data)
    
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> 'ListCollectionsTool':
        """Create a tool from a JSON string."""
        return cls.from_dict(json.loads(data))

