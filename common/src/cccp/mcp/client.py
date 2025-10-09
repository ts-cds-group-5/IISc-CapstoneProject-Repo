import asyncio
import json
import os
import subprocess
from typing import Any, Dict, List, Optional
from cccp.core.logging import get_logger
from cccp.core.config import get_mcp_server_path

#Flow
# Connect: Starts postgresql-mcp-server subprocess
# Initialize: Sends MCP initialization request
# Query: Sends SQL query via MCP tools/call method
# Response: Parses MCP JSON-RPC response

class MCPPostgresClient:
    """Client for PostgreSQL MCP server using MCP protocol."""
    
    def __init__(self):
        self.mcp_host = os.getenv("MCP_POSTGRES_HOST", "localhost")
        self.mcp_port = int(os.getenv("MCP_POSTGRES_PORT", "8001"))
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.postgres_user = os.getenv("POSTGRES_USER", "postgres")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.postgres_database = os.getenv("POSTGRES_DB", "postgres")
        self.logger = get_logger(__name__)
        self.mcp_process = None
        self.session = None
        
    async def query(self, sql: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Execute SQL query using MCP protocol."""
        try:
            if not self.session:
                await self.connect()
            
            # Prepare MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "execute_query",
                    "arguments": {
                        "sql": sql,
                        "params": params or {}
                    }
                }
            }
            
            # Send request to MCP server
            response = await self._send_mcp_request(mcp_request)
            
            if "error" in response:
                raise Exception(f"MCP server error: {response['error']}")
            
            # Parse response
            result = response.get("result", {})
            content = result.get("content", [])
            
            # Parse the JSON response from MCP server
            if content and len(content) > 0:
                text_content = content[0].get("text", "[]")
                try:
                    rows = json.loads(text_content)
                    return rows
                except json.JSONDecodeError:
                    return []
            return []
            
        except Exception as e:
            self.logger.error(f"MCP query error: {str(e)}")
            raise
    
    async def connect(self):
        """Establish MCP server connection."""
        try:
            # Get MCP server path from config (with fallback to project root)
            mcp_server_path = get_mcp_server_path()
            self.logger.info(f"Using MCP server at: {mcp_server_path}")
            
            # Start MCP server process
            cmd = [
                "python", mcp_server_path
            ]
            
            # Set environment for the MCP server
            env = os.environ.copy()
            env["POSTGRES_CONNECTION_STRING"] = f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
            
            self.mcp_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Initialize MCP session
            init_request = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "cccp-postgres-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self._send_mcp_request(init_request)
            
            if "error" in response:
                raise Exception(f"MCP initialization error: {response['error']}")
            
            self.session = True
            self.logger.info(f"Connected to MCP PostgreSQL server at {self.mcp_host}:{self.mcp_port}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {str(e)}")
            raise
    
    async def _send_mcp_request(self, request: Dict) -> Dict:
        """Send request to MCP server and get response."""
        if not self.mcp_process:
            raise Exception("MCP server not connected")
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.mcp_process.stdin.write(request_json.encode())
            await self.mcp_process.stdin.drain()
            
            # Read response
            response_line = await self.mcp_process.stdout.readline()
            response_json = response_line.decode().strip()
            
            return json.loads(response_json)
            
        except Exception as e:
            self.logger.error(f"Error communicating with MCP server: {str(e)}")
            raise
    
    async def close(self):
        """Close MCP server connection."""
        if self.mcp_process:
            self.mcp_process.terminate()
            await self.mcp_process.wait()
            self.mcp_process = None
            self.session = None
            self.logger.info("MCP server connection closed")