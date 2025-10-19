"""Unit tests for catalog tools."""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from cccp.tools.catalog.list_collections import ListCollectionsTool
from cccp.tools.catalog.get_catalog import GetCatalogTool
from cccp.tools.catalog.search_products import SearchProductsTool
from cccp.tools.catalog.catalog_utils import (
    build_filter_where_clauses,
    format_price,
    format_catalog_json,
    format_catalog_text
)
from cccp.core.exceptions import ToolError


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_collections_data():
    """Sample collections data from README-docker.md."""
    return [
        {
            "collection_id": 2,
            "collection_name": "Electronics",
            "collection_code": "COLL_ELEC",
            "product_count": 6
        },
        {
            "collection_id": 3,
            "collection_name": "Furniture",
            "collection_code": "COLL_FURN",
            "product_count": 6
        },
        {
            "collection_id": 4,
            "collection_name": "Books",
            "collection_code": "COLL_BOOK",
            "product_count": 6
        },
        {
            "collection_id": 5,
            "collection_name": "Clothing",
            "collection_code": "COLL_CLOTH",
            "product_count": 6
        }
    ]


@pytest.fixture
def mock_catalog_data():
    """Sample product catalog data."""
    return [
        {
            "collection_id": 2,
            "collection_name": "Electronics",
            "product_id": 1,
            "product_name": "Samsung Galaxy M35 5G (6GB/128GB)",
            "product_description": "Brand: Samsung | 6.6\" sAMOLED, Exynos chipset",
            "currency": "INR",
            "product_price": 16999.00,
            "product_stock_qty": 60
        },
        {
            "collection_id": 2,
            "collection_name": "Electronics",
            "product_id": 2,
            "product_name": "Lenovo IdeaPad Slim 3 (Ryzen 5, 16GB/512GB)",
            "product_description": "Brand: Lenovo | 15.6\" FHD, Ryzen 5 5500U",
            "currency": "INR",
            "product_price": 52990.00,
            "product_stock_qty": 25
        },
        {
            "collection_id": 3,
            "collection_name": "Furniture",
            "product_id": 7,
            "product_name": "Nilkamal Astra Office Chair (Ergonomic)",
            "product_description": "Brand: Nilkamal | Mesh back, lumbar support",
            "currency": "INR",
            "product_price": 7990.00,
            "product_stock_qty": 40
        }
    ]


@pytest.fixture
def mock_mcp_client():
    """Mock MCP Postgres client."""
    mock_client = AsyncMock()
    mock_client.connect = AsyncMock()
    mock_client.query = AsyncMock()
    mock_client.close = AsyncMock()
    return mock_client


# ============================================================================
# Tests for ListCollectionsTool
# ============================================================================

class TestListCollectionsTool:
    """Test cases for ListCollectionsTool."""
    
    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = ListCollectionsTool()
        assert tool.tool_name == "listcollections"
        assert tool._get_name() == "listcollections"
        assert "collections" in tool._get_description().lower()
    
    @patch('cccp.tools.catalog.list_collections.MCPPostgresClient')
    def test_list_collections_success(self, mock_mcp_class, mock_collections_data):
        """Test successful collections listing."""
        # Setup mock
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.query = AsyncMock(return_value=mock_collections_data)
        mock_client.close = AsyncMock()
        mock_mcp_class.return_value = mock_client
        
        # Execute
        tool = ListCollectionsTool()
        result = tool.run()
        
        # Verify
        assert "Electronics" in result
        assert "Furniture" in result
        assert "Books" in result
        assert "Clothing" in result
        assert "4 collections" in result or "24 products" in result
    
    @patch('cccp.tools.catalog.list_collections.MCPPostgresClient')
    def test_list_collections_empty_db(self, mock_mcp_class):
        """Test when no collections in database."""
        # Setup mock
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.query = AsyncMock(return_value=[])
        mock_client.close = AsyncMock()
        mock_mcp_class.return_value = mock_client
        
        # Execute
        tool = ListCollectionsTool()
        result = tool.run()
        
        # Verify
        assert "No collections found" in result
    
    @patch('cccp.tools.catalog.list_collections.MCPPostgresClient')
    def test_list_collections_db_error(self, mock_mcp_class):
        """Test database error handling."""
        # Setup mock to raise error
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.query = AsyncMock(side_effect=Exception("Database connection failed"))
        mock_client.close = AsyncMock()
        mock_mcp_class.return_value = mock_client
        
        # Execute and verify error
        tool = ListCollectionsTool()
        with pytest.raises(ToolError):
            tool.run()


# ============================================================================
# Tests for GetCatalogTool
# ============================================================================

class TestGetCatalogTool:
    """Test cases for GetCatalogTool."""
    
    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = GetCatalogTool()
        assert tool.tool_name == "getcatalog"
        assert tool._get_name() == "getcatalog"
        assert "catalog" in tool._get_description().lower()
    
    @patch('cccp.tools.catalog.get_catalog.MCPPostgresClient')
    def test_get_catalog_no_filters(self, mock_mcp_class, mock_catalog_data):
        """Test catalog retrieval without filters."""
        # Setup mock
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.query = AsyncMock(return_value=mock_catalog_data)
        mock_client.close = AsyncMock()
        mock_mcp_class.return_value = mock_client
        
        # Execute
        tool = GetCatalogTool()
        result = tool.run()
        
        # Verify
        assert "Samsung Galaxy" in result
        assert "Lenovo IdeaPad" in result
        assert "Nilkamal" in result
    
    @patch('cccp.tools.catalog.get_catalog.MCPPostgresClient')
    def test_get_catalog_with_collection_filter(self, mock_mcp_class, mock_catalog_data):
        """Test filtering by collection."""
        # Setup mock - filter to only Electronics
        electronics_data = [item for item in mock_catalog_data if item['collection_name'] == 'Electronics']
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.query = AsyncMock(return_value=electronics_data)
        mock_client.close = AsyncMock()
        mock_mcp_class.return_value = mock_client
        
        # Execute
        tool = GetCatalogTool()
        result = tool.run(collection_name="Electronics")
        
        # Verify
        assert "Electronics" in result
        assert "Samsung" in result or "Lenovo" in result
    
    @patch('cccp.tools.catalog.get_catalog.MCPPostgresClient')
    def test_get_catalog_with_price_range(self, mock_mcp_class, mock_catalog_data):
        """Test price range filtering."""
        # Setup mock - filter by price
        filtered_data = [item for item in mock_catalog_data if item['product_price'] <= 20000]
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.query = AsyncMock(return_value=filtered_data)
        mock_client.close = AsyncMock()
        mock_mcp_class.return_value = mock_client
        
        # Execute
        tool = GetCatalogTool()
        result = tool.run(max_price=20000.0)
        
        # Verify
        assert "Samsung Galaxy" in result  # 16999
        assert "Nilkamal" in result  # 7990
        # Lenovo (52990) should not be present if filtering works
    
    def test_get_catalog_invalid_price_range(self):
        """Test invalid price range validation."""
        tool = GetCatalogTool()
        with pytest.raises(ToolError) as exc_info:
            tool.run(min_price=10000.0, max_price=5000.0)
        
        assert "min_price" in str(exc_info.value).lower()
        assert "max_price" in str(exc_info.value).lower()
    
    @patch('cccp.tools.catalog.get_catalog.MCPPostgresClient')
    def test_get_catalog_no_results(self, mock_mcp_class):
        """Test when no products match filters."""
        # Setup mock
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.query = AsyncMock(return_value=[])
        mock_client.close = AsyncMock()
        mock_mcp_class.return_value = mock_client
        
        # Execute
        tool = GetCatalogTool()
        result = tool.run(min_price=1000000.0)  # Unrealistic price
        
        # Verify
        assert "No products found" in result


# ============================================================================
# Tests for SearchProductsTool
# ============================================================================

class TestSearchProductsTool:
    """Test cases for SearchProductsTool."""
    
    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = SearchProductsTool()
        assert tool.tool_name == "searchproducts"
        assert tool._get_name() == "searchproducts"
        assert "search" in tool._get_description().lower()
    
    def test_search_products_missing_keyword(self):
        """Test that keyword is required."""
        tool = SearchProductsTool()
        with pytest.raises(ToolError) as exc_info:
            tool.run(keyword=None)
        
        assert "keyword" in str(exc_info.value).lower()
        assert "required" in str(exc_info.value).lower()
    
    def test_search_products_short_keyword(self):
        """Test keyword minimum length validation."""
        tool = SearchProductsTool()
        with pytest.raises(ToolError) as exc_info:
            tool.run(keyword="a")
        
        assert "keyword" in str(exc_info.value).lower()
    
    @patch('cccp.tools.catalog.search_products.MCPPostgresClient')
    def test_search_products_success(self, mock_mcp_class, mock_catalog_data):
        """Test successful product search."""
        # Setup mock - search for "Samsung"
        search_results = [item for item in mock_catalog_data if "Samsung" in item['product_name']]
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.query = AsyncMock(return_value=search_results)
        mock_client.close = AsyncMock()
        mock_mcp_class.return_value = mock_client
        
        # Execute
        tool = SearchProductsTool()
        result = tool.run(keyword="Samsung")
        
        # Verify
        assert "Samsung Galaxy" in result
        assert "Found" in result
    
    @patch('cccp.tools.catalog.search_products.MCPPostgresClient')
    def test_search_products_no_results(self, mock_mcp_class):
        """Test search with no matching products."""
        # Setup mock
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.query = AsyncMock(return_value=[])
        mock_client.close = AsyncMock()
        mock_mcp_class.return_value = mock_client
        
        # Execute
        tool = SearchProductsTool()
        result = tool.run(keyword="NonExistentProduct")
        
        # Verify
        assert "No products found" in result
        assert "NonExistentProduct" in result
    
    @patch('cccp.tools.catalog.search_products.MCPPostgresClient')
    def test_search_with_filters(self, mock_mcp_class, mock_catalog_data):
        """Test search with additional filters."""
        # Setup mock - search with collection filter
        filtered_results = [
            item for item in mock_catalog_data 
            if item['collection_name'] == 'Electronics'
        ]
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.query = AsyncMock(return_value=filtered_results)
        mock_client.close = AsyncMock()
        mock_mcp_class.return_value = mock_client
        
        # Execute
        tool = SearchProductsTool()
        result = tool.run(keyword="laptop", collection_name="Electronics", max_price=60000.0)
        
        # Verify
        assert "Electronics" in result or "Found" in result


# ============================================================================
# Tests for Catalog Utilities
# ============================================================================

class TestCatalogUtils:
    """Test cases for catalog utility functions."""
    
    def test_build_filter_where_clauses_empty(self):
        """Test building WHERE clauses with no filters."""
        filters = {'in_stock_only': False}
        where_clauses, params = build_filter_where_clauses(filters)
        
        assert len(where_clauses) == 0
        assert len(params) == 0
    
    def test_build_filter_where_clauses_stock_only(self):
        """Test in_stock_only filter."""
        filters = {'in_stock_only': True}
        where_clauses, params = build_filter_where_clauses(filters)
        
        assert len(where_clauses) == 1
        assert "product_stock_qty > 0" in where_clauses[0]
    
    def test_build_filter_where_clauses_collection(self):
        """Test collection name filter with positional parameters."""
        filters = {'collection_name': 'Electronics', 'in_stock_only': False}
        where_clauses, params = build_filter_where_clauses(filters)
        
        assert len(where_clauses) == 1
        assert "c.name = $1" in where_clauses[0]  # Positional parameter
        assert params['1'] == 'Electronics'  # Numeric string key
    
    def test_build_filter_where_clauses_price_range(self):
        """Test price range filters with positional parameters."""
        filters = {
            'min_price': 1000.0,
            'max_price': 5000.0,
            'in_stock_only': False
        }
        where_clauses, params = build_filter_where_clauses(filters)
        
        assert len(where_clauses) == 2
        assert "$1" in where_clauses[0]  # First positional param
        assert "$2" in where_clauses[1]  # Second positional param
        assert params['1'] == 1000.0
        assert params['2'] == 5000.0
    
    def test_build_filter_where_clauses_keyword(self):
        """Test keyword search filter with positional parameters."""
        filters = {'keyword': 'laptop', 'in_stock_only': False}
        where_clauses, params = build_filter_where_clauses(filters)
        
        assert len(where_clauses) == 1
        assert "ILIKE" in where_clauses[0]
        assert "$1" in where_clauses[0]  # Positional parameter
        assert params['1'] == '%laptop%'
    
    def test_build_filter_where_clauses_combined(self):
        """Test multiple filters with correct parameter ordering."""
        filters = {
            'collection_name': 'Books',
            'max_price': 1000.0,
            'keyword': 'history',
            'in_stock_only': True
        }
        where_clauses, params = build_filter_where_clauses(filters)
        
        # Should have: stock filter (no param) + collection ($1) + price ($2) + keyword ($3)
        assert len(where_clauses) == 4
        assert "product_stock_qty > 0" in where_clauses[0]
        assert "c.name = $1" in where_clauses[1]
        assert "$2" in where_clauses[2]
        assert "$3" in where_clauses[3]
        
        # Verify parameter order
        assert params['1'] == 'Books'
        assert params['2'] == 1000.0
        assert params['3'] == '%history%'
        assert len(params) == 3  # Three positional params
    
    def test_format_price_inr(self):
        """Test INR price formatting."""
        result = format_price('INR', 16999.00)
        assert '₹' in result
        assert '16,999.00' in result
    
    def test_format_price_usd(self):
        """Test USD price formatting."""
        result = format_price('USD', 199.99)
        assert '$' in result
        assert '199.99' in result
    
    def test_format_catalog_json(self, mock_catalog_data):
        """Test JSON catalog formatting."""
        result = format_catalog_json(mock_catalog_data)
        
        assert 'total_collections' in result
        assert 'total_products' in result
        assert 'collections' in result
        assert result['total_products'] == len(mock_catalog_data)
        assert len(result['collections']) > 0
    
    def test_format_catalog_text(self, mock_catalog_data):
        """Test text catalog formatting."""
        result = format_catalog_text(mock_catalog_data)
        
        assert "Product Catalog" in result
        assert "Electronics" in result
        assert "Samsung Galaxy" in result
        assert "₹" in result  # Price formatting
    
    def test_format_catalog_text_empty(self):
        """Test formatting empty catalog."""
        result = format_catalog_text([])
        assert "No products found" in result


# ============================================================================
# Integration-like Tests (with mocked DB but full workflow)
# ============================================================================

class TestCatalogToolsIntegration:
    """Integration-style tests for catalog tools."""
    
    @patch('cccp.tools.catalog.list_collections.MCPPostgresClient')
    @patch('cccp.tools.catalog.get_catalog.MCPPostgresClient')
    def test_workflow_list_then_get_catalog(self, mock_get_mcp, mock_list_mcp, 
                                           mock_collections_data, mock_catalog_data):
        """Test workflow: list collections, then get specific catalog."""
        # Setup mocks
        mock_list_client = AsyncMock()
        mock_list_client.connect = AsyncMock()
        mock_list_client.query = AsyncMock(return_value=mock_collections_data)
        mock_list_client.close = AsyncMock()
        mock_list_mcp.return_value = mock_list_client
        
        mock_get_client = AsyncMock()
        mock_get_client.connect = AsyncMock()
        mock_get_client.query = AsyncMock(return_value=mock_catalog_data)
        mock_get_client.close = AsyncMock()
        mock_get_mcp.return_value = mock_get_client
        
        # Execute workflow
        list_tool = ListCollectionsTool()
        collections_result = list_tool.run()
        
        assert "Electronics" in collections_result
        
        catalog_tool = GetCatalogTool()
        catalog_result = catalog_tool.run(collection_name="Electronics")
        
        assert "Samsung" in catalog_result or "product" in catalog_result.lower()


class TestOrderParameterExtraction:
    """Test cases for order parameter extraction from user queries."""
    
    def test_extract_cart_id_with_number(self):
        """Test extracting cart ID with just a number."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        
        # Test "cart 454"
        params = agent._extract_parameters("What's in cart 454?", "getorder")
        assert params.get("cart_id") == "454"
        
        # Test "order 123"
        params = agent._extract_parameters("Check order 123", "getorder")
        assert params.get("cart_id") == "123"
    
    def test_extract_cart_id_alphanumeric(self):
        """Test extracting alphanumeric cart IDs."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        
        # Test "cart454"
        params = agent._extract_parameters("Show me cart454", "getorder")
        assert params.get("cart_id") == "cart454"
        
        # Test "cartabc123"
        params = agent._extract_parameters("What about cartabc123?", "getorder")
        assert params.get("cart_id") == "cartabc123"
    
    def test_extract_email_from_query(self):
        """Test extracting email from query text."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        
        params = agent._extract_parameters("Order for john.doe@example.com", "getorder")
        assert params.get("customer_email") == "john.doe@example.com"
    
    def test_vague_query_uses_session_email(self):
        """Test that vague queries use session email."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        # Set up user session
        agent.user_session = {
            'user_id': '12345',
            'name': 'John Doe',
            'email': 'john@example.com',
            'mobile': '1234567890'
        }
        
        # Test "I placed an order earlier"
        params = agent._extract_parameters("I placed an order earlier", "getorder")
        assert params.get("customer_email") == "john@example.com"
        
        # Test "my order"
        params = agent._extract_parameters("my order", "getorder")
        assert params.get("customer_email") == "john@example.com"
        
        # Test "order status"
        params = agent._extract_parameters("order status", "getorder")
        assert params.get("customer_email") == "john@example.com"
    
    def test_vague_query_uses_session_name_if_no_email(self):
        """Test that vague queries use session name if email not available."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        # Set up user session without email
        agent.user_session = {
            'user_id': '12345',
            'name': 'John Doe',
            'mobile': '1234567890'
        }
        
        params = agent._extract_parameters("I placed an order earlier", "getorder")
        assert params.get("customer_full_name") == "John Doe"
    
    def test_avoids_extracting_vague_words(self):
        """Test that vague words like 'earlier' are not extracted as cart_id."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        agent.user_session = {
            'email': 'test@example.com'
        }
        
        # Should not extract "earlier" as cart_id
        params = agent._extract_parameters("I placed an order earlier", "getorder")
        assert "cart_id" not in params or params.get("cart_id") != "earlier"
        assert params.get("customer_email") == "test@example.com"  # Should fallback to email
        
        # Should not extract "yesterday" as cart_id
        params = agent._extract_parameters("my order yesterday", "getorder")
        assert "cart_id" not in params or params.get("cart_id") != "yesterday"
    
    def test_specific_cart_id_overrides_session(self):
        """Test that specific cart ID takes precedence over session."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        agent.user_session = {
            'email': 'test@example.com'
        }
        
        # Specific cart ID should be used instead of session email
        params = agent._extract_parameters("Show me cart 789", "getorder")
        assert params.get("cart_id") == "789"
        assert "customer_email" not in params
    
    def test_various_order_query_formats(self):
        """Test various ways users might ask about orders."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        agent.user_session = {'email': 'user@example.com'}
        
        queries_should_use_email = [
            "What's my order status?",
            "where is my order",
            "I placed an order",
            "my purchase",
            "what about my cart",
            "order details",
            "check my order",
        ]
        
        for query in queries_should_use_email:
            params = agent._extract_parameters(query, "getorder")
            assert params.get("customer_email") == "user@example.com", \
                f"Query '{query}' should use session email"
    
    def test_no_session_no_cart_id_returns_empty(self):
        """Test that queries with no cart_id and no session return empty."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        # No user session
        
        params = agent._extract_parameters("I placed an order earlier", "getorder")
        # Should be empty dict (tool will fail with appropriate error)
        assert params == {}
    
    def test_order_query_with_properties_uses_session(self):
        """Test queries about order properties use session email."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        agent.user_session = {'email': 'user@example.com'}
        
        # Test queries about order properties
        queries_with_properties = [
            "Do I have an order with total 330?",
            "Is there an order for 199?",
            "My order total was 500",
            "order amount 1000",
            "purchase for 250",
        ]
        
        for query in queries_with_properties:
            params = agent._extract_parameters(query, "getorder")
            assert params.get("customer_email") == "user@example.com", \
                f"Query '{query}' should use session email"
    
    def test_order_keywords_trigger_session_lookup(self):
        """Test that order-related keywords trigger session email usage."""
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        agent.user_session = {'email': 'user@example.com'}
        
        # Various order-related keywords
        test_queries = [
            ("shipment details", "shipment"),
            ("delivery status", "delivery"),
            ("tracking information", "tracking"),
            ("invoice please", "invoice"),
            ("receipt for my purchase", "receipt"),
        ]
        
        for query, keyword in test_queries:
            params = agent._extract_parameters(query, "getorder")
            assert params.get("customer_email") == "user@example.com", \
                f"Query with keyword '{keyword}' should use session email"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

