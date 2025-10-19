#!/usr/bin/env python3
"""
Simple MCP PostgreSQL Server
Implements the Model Context Protocol for PostgreSQL database access.
"""

import asyncio
import json
import sys
import os
import asyncpg
from typing import Any, Dict, List, Optional


class MCPServer:
    """Simple MCP Server for PostgreSQL."""
    
    def __init__(self):
        self.db_pool: Optional[asyncpg.Pool] = None
        self.connection_string = os.getenv(
            "POSTGRES_CONNECTION_STRING", 
            "postgresql://postgres:postgres@database:5432/postgres"
        )
    
    async def initialize_db(self):
        """Initialize database connection pool."""
        try:
            self.db_pool = await asyncpg.create_pool(self.connection_string)
            print(f"Connected to PostgreSQL database", file=sys.stderr)
        except Exception as e:
            print(f"Failed to connect to database: {e}", file=sys.stderr)
            raise
    
    async def close_db(self):
        """Close database connection pool."""
        if self.db_pool:
            await self.db_pool.close()
    
    async def execute_query(self, sql: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Execute SQL query and return results."""
        if not self.db_pool:
            raise Exception("Database not connected")
        
        try:
            async with self.db_pool.acquire() as conn:
                if params:
                    rows = await conn.fetch(sql, *params.values())
                else:
                    rows = await conn.fetch(sql)
                
                # Convert asyncpg.Record objects to dictionaries
                result = []
                for row in rows:
                    result.append(dict(row))
                
                return result
        except Exception as e:
            print(f"Query execution error: {e}", file=sys.stderr)
            raise
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "simple-postgres-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "execute_query",
                                "description": "Execute a SQL query against the PostgreSQL database",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "sql": {
                                            "type": "string",
                                            "description": "SQL query to execute"
                                        },
                                        "params": {
                                            "type": "object",
                                            "description": "Query parameters (optional)",
                                            "additionalProperties": True
                                        }
                                    },
                                    "required": ["sql"]
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "execute_query":
                    sql = arguments.get("sql")
                    query_params = arguments.get("params")
                    
                    if not sql:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32602,
                                "message": "Missing required parameter: sql"
                            }
                        }
                    
                    try:
                        results = await self.execute_query(sql, query_params)
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(results, default=str, indent=2)
                                    }
                                ]
                            }
                        }
                    except Exception as e:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32603,
                                "message": f"Query execution failed: {str(e)}"
                            }
                        }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run(self):
        """Run the MCP server."""
        await self.initialize_db()
        
        try:
            # Read from stdin in a blocking way using a thread
            import threading
            import queue
            
            input_queue = queue.Queue()
            
            def read_stdin():
                while True:
                    try:
                        line = sys.stdin.readline()
                        if not line:
                            break
                        input_queue.put(line.strip())
                    except:
                        break
            
            # Start stdin reader thread
            stdin_thread = threading.Thread(target=read_stdin, daemon=True)
            stdin_thread.start()
            
            while True:
                try:
                    # Wait for input with timeout
                    try:
                        line = input_queue.get(timeout=1.0)
                        if not line:
                            continue
                    except queue.Empty:
                        continue
                    
                    try:
                        request = json.loads(line)
                        response = await self.handle_request(request)
                        print(json.dumps(response))
                        sys.stdout.flush()
                    except json.JSONDecodeError as e:
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32700,
                                "message": f"Parse error: {str(e)}"
                            }
                        }
                        print(json.dumps(error_response))
                        sys.stdout.flush()
                
                except Exception as e:
                    print(f"Error processing request: {e}", file=sys.stderr)
                    continue
        
        except KeyboardInterrupt:
            pass
        finally:
            await self.close_db()


async def main():
    """Main entry point."""
    server = MCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
