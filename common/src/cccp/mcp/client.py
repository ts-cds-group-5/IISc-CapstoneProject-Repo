import asyncpg
import os
from typing import Any, Dict, List, Optional
from cccp.core.logging import get_logger

class MCPPostgresClient:
    """Client for PostgreSQL MCP server using asyncpg."""
    
    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.database = os.getenv("POSTGRES_DB", "postgres")
        self.logger = get_logger(__name__)
        self.connection = None
        
    async def query(self, sql: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Execute SQL query using asyncpg."""
        try:
            if not self.connection:
                await self.connect()
            
            # Convert params dict to list for asyncpg
            param_values = list(params.values()) if params else []
            
            rows = await self.connection.fetch(sql, *param_values)
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Database query error: {str(e)}")
            raise
    
    async def connect(self):
        """Establish database connection."""
        try:
            self.connection = await asyncpg.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.logger.info(f"Connected to PostgreSQL at {self.host}:{self.port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    async def close(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
            self.logger.info("Database connection closed")