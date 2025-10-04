#!/usr/bin/env python3
"""
Test script for MCP PostgreSQL integration.

This script tests:
1. MCP server connectivity
2. Database queries through MCP protocol
3. Cart retrieval functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from cccp.mcp.client import MCPPostgresClient
from cccp.core.logging import setup_logging, get_logger

async def test_mcp_connection():
    """Test basic MCP server connection."""
    logger = get_logger(__name__)
    logger.info("Testing MCP PostgreSQL connection...")
    
    client = MCPPostgresClient()
    try:
        await client.connect()
        logger.info("✅ MCP server connection successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP server connection failed: {str(e)}")
        return False
    finally:
        await client.close()

async def test_mcp_query():
    """Test SQL query through MCP protocol."""
    logger = get_logger(__name__)
    logger.info("Testing MCP SQL query...")
    
    client = MCPPostgresClient()
    try:
        await client.connect()
        
        # Test basic query
        result = await client.query("SELECT version()")
        logger.info(f"✅ PostgreSQL version via MCP: {result[0]['version'] if result else 'No result'}")
        
        # Test table listing
        tables_result = await client.query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = [row['table_name'] for row in tables_result]
        logger.info(f"✅ Tables found via MCP: {tables}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP query failed: {str(e)}")
        return False
    finally:
        await client.close()

async def test_cart_retrieval():
    """Test cart retrieval through MCP."""
    logger = get_logger(__name__)
    logger.info("Testing cart retrieval via MCP...")
    
    client = MCPPostgresClient()
    try:
        await client.connect()
        
        # Test cart query (using cart_id = 2 from our test data)
        cart_result = await client.query("""
            SELECT cart_id, customer_email, customer_full_name,
                   user_ip, grand_total, shipping_note
            FROM cart
            WHERE cart_id = $1 AND status = 'true'
            LIMIT 1
        """, {"cart_id": 2})
        
        if cart_result:
            cart = cart_result[0]
            logger.info(f"✅ Cart retrieved via MCP: {cart}")
            return True
        else:
            logger.warning("⚠️ No cart found with cart_id=2")
            return False
            
    except Exception as e:
        logger.error(f"❌ Cart retrieval via MCP failed: {str(e)}")
        return False
    finally:
        await client.close()

async def main():
    """Main test function."""
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("🚀 Starting MCP Integration Tests")
    logger.info("=" * 50)
    
    # Test 1: Connection
    logger.info("\n1. Testing MCP Server Connection")
    connection_ok = await test_mcp_connection()
    
    if not connection_ok:
        logger.error("❌ MCP server connection failed. Please check:")
        logger.error("   - Docker containers are running")
        logger.error("   - postgresql-mcp-server is installed")
        logger.error("   - Environment variables are set correctly")
        return
    
    # Test 2: Basic Query
    logger.info("\n2. Testing MCP SQL Query")
    query_ok = await test_mcp_query()
    
    # Test 3: Cart Retrieval
    logger.info("\n3. Testing Cart Retrieval via MCP")
    cart_ok = await test_cart_retrieval()
    
    logger.info("\n" + "=" * 50)
    logger.info("🎉 MCP Integration Tests Complete!")
    
    # Summary
    logger.info(f"\nSummary:")
    logger.info(f"  - MCP Connection: {'✅ OK' if connection_ok else '❌ FAILED'}")
    logger.info(f"  - SQL Query: {'✅ OK' if query_ok else '❌ FAILED'}")
    logger.info(f"  - Cart Retrieval: {'✅ OK' if cart_ok else '❌ FAILED'}")
    
    if connection_ok and query_ok and cart_ok:
        logger.info("\n🎉 All MCP tests passed! Ready for end-to-end testing.")
    else:
        logger.error("\n❌ Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    asyncio.run(main())
