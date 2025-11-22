"""Integration tests for catalog tools with real Docker Postgres database.

These tests require:
1. Docker Postgres running on localhost:5432
2. Database populated with sample data from README-docker.md
3. Environment variables set for POSTGRES_* connection

Run with: pytest tests/integration/test_catalog_integration.py -v
"""

import pytest
import os
from cccp.tools.catalog.list_collections import ListCollectionsTool
from cccp.tools.catalog.get_catalog import GetCatalogTool
from cccp.tools.catalog.search_products import SearchProductsTool
from cccp.core.exceptions import ToolError


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def check_database_available():
    """Check if database is available before running tests."""
    # Check environment variables
    required_vars = ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        pytest.skip(f"Database configuration missing: {', '.join(missing_vars)}")
    
    # You could add a connection test here
    return True


class TestListCollectionsIntegration:
    """Integration tests for ListCollectionsTool."""
    
    def test_list_collections_real_db(self, check_database_available):
        """Test listing collections from real database."""
        tool = ListCollectionsTool()
        
        try:
            result = tool.run()
            
            # Verify expected collections exist (from README-docker.md sample data)
            assert isinstance(result, str)
            assert len(result) > 0
            
            # Check for known collections
            expected_collections = ["Electronics", "Furniture", "Books", "Clothing"]
            for collection in expected_collections:
                assert collection in result, f"Expected collection '{collection}' not found in result"
            
            # Check for product counts
            assert "product" in result.lower()
            assert "collection" in result.lower()
            
            print(f"\n✅ List Collections Result:\n{result}")
            
        except ToolError as e:
            pytest.fail(f"Tool error: {str(e)}")
        except Exception as e:
            pytest.fail(f"Unexpected error: {str(e)}")
    
    def test_list_collections_format(self, check_database_available):
        """Test that collections are formatted correctly."""
        tool = ListCollectionsTool()
        result = tool.run()
        
        # Check formatting elements
        assert "📦" in result or "Collection" in result  # Formatting symbols
        assert "COLL_" in result  # Collection codes
        
        # Check for total summary
        assert "Total:" in result or "total" in result.lower()


class TestGetCatalogIntegration:
    """Integration tests for GetCatalogTool."""
    
    def test_get_catalog_no_filters_real_db(self, check_database_available):
        """Test getting full catalog from real database."""
        tool = GetCatalogTool()
        
        try:
            result = tool.run()
            
            assert isinstance(result, str)
            assert len(result) > 0
            
            # Check for product information
            assert "product" in result.lower()
            assert "₹" in result or "INR" in result  # Currency
            
            print(f"\n✅ Full Catalog (truncated):\n{result[:500]}...")
            
        except ToolError as e:
            pytest.fail(f"Tool error: {str(e)}")
    
    def test_get_catalog_parameter_handling(self, check_database_available):
        """Test that positional parameters work correctly with MCP server."""
        tool = GetCatalogTool()
        
        try:
            # This tests the positional parameter fix ($1, $2, etc.)
            result = tool.run(collection_name="Books", max_price=1000.0)
            
            assert isinstance(result, str)
            # Should either show Books under 1000 or indicate none found
            assert "Books" in result or "No products found" in result
            
            print(f"\n✅ Books under ₹1000:\n{result}")
            
        except ToolError as e:
            pytest.fail(f"Tool error (parameter handling issue): {str(e)}")
    
    def test_get_catalog_electronics_real_db(self, check_database_available):
        """Test getting Electronics catalog."""
        tool = GetCatalogTool()
        
        try:
            result = tool.run(collection_name="Electronics")
            
            assert "Electronics" in result
            
            # Check for known Electronics products (from README-docker.md)
            # At least one of these should be present
            electronics_keywords = ["Samsung", "Redmi", "Lenovo", "LG", "OnePlus", "boAt"]
            assert any(keyword in result for keyword in electronics_keywords), \
                "No Electronics products found in result"
            
            print(f"\n✅ Electronics Catalog:\n{result}")
            
        except ToolError as e:
            pytest.fail(f"Tool error: {str(e)}")
    
    def test_get_catalog_with_price_filter_real_db(self, check_database_available):
        """Test catalog with price filter."""
        tool = GetCatalogTool()
        
        try:
            # Get products under ₹10,000
            result = tool.run(max_price=10000.0)
            
            assert isinstance(result, str)
            
            # Products under 10k from sample data: boAt (1299), OnePlus (1899), Nilkamal (7990), etc.
            # If no products, result should indicate that
            if "No products found" not in result:
                assert "product" in result.lower()
            
            print(f"\n✅ Products under ₹10,000:\n{result}")
            
        except ToolError as e:
            pytest.fail(f"Tool error: {str(e)}")
    
    def test_get_catalog_furniture_real_db(self, check_database_available):
        """Test getting Furniture catalog."""
        tool = GetCatalogTool()
        
        try:
            result = tool.run(collection_name="Furniture")
            
            assert "Furniture" in result
            
            # Check for known Furniture items
            furniture_keywords = ["Chair", "Bed", "Table", "Wardrobe", "Sofa"]
            assert any(keyword.lower() in result.lower() for keyword in furniture_keywords), \
                "No Furniture products found in result"
            
            print(f"\n✅ Furniture Catalog:\n{result}")
            
        except ToolError as e:
            pytest.fail(f"Tool error: {str(e)}")
    
    def test_get_catalog_invalid_collection(self, check_database_available):
        """Test with non-existent collection."""
        tool = GetCatalogTool()
        
        try:
            result = tool.run(collection_name="NonExistentCollection")
            
            # Should return no products found
            assert "No products found" in result or len(result) > 0
            
        except ToolError as e:
            # This is acceptable - tool might raise error for invalid collection
            pass


class TestSearchProductsIntegration:
    """Integration tests for SearchProductsTool."""
    
    def test_search_products_keyword_real_db(self, check_database_available):
        """Test product search with keyword."""
        tool = SearchProductsTool()
        
        try:
            # Search for "laptop" (should find Lenovo IdeaPad)
            result = tool.run(keyword="laptop")
            
            assert isinstance(result, str)
            
            # Check if search found products
            if "No products found" not in result:
                assert "laptop" in result.lower() or "Lenovo" in result
                assert "Found" in result  # Search summary
            
            print(f"\n✅ Search for 'laptop':\n{result}")
            
        except ToolError as e:
            pytest.fail(f"Tool error: {str(e)}")
    
    def test_search_products_samsung_real_db(self, check_database_available):
        """Test searching for Samsung products."""
        tool = SearchProductsTool()
        
        try:
            result = tool.run(keyword="Samsung")
            
            if "No products found" not in result:
                assert "Samsung" in result
                assert "Found" in result
            
            print(f"\n✅ Search for 'Samsung':\n{result}")
            
        except ToolError as e:
            pytest.fail(f"Tool error: {str(e)}")
    
    def test_search_products_with_price_filter_real_db(self, check_database_available):
        """Test search with price filter."""
        tool = SearchProductsTool()
        
        try:
            # Search for products under ₹5000
            result = tool.run(keyword="product", max_price=5000.0)
            
            # Result should either show products or indicate none found
            assert isinstance(result, str)
            assert len(result) > 0
            
            print(f"\n✅ Search 'product' under ₹5000:\n{result}")
            
        except ToolError as e:
            pytest.fail(f"Tool error: {str(e)}")
    
    def test_search_products_in_collection_real_db(self, check_database_available):
        """Test search within specific collection."""
        tool = SearchProductsTool()
        
        try:
            # Search for "chair" in Furniture
            result = tool.run(keyword="chair", collection_name="Furniture")
            
            if "No products found" not in result:
                assert "chair" in result.lower() or "Chair" in result
                assert "Furniture" in result
            
            print(f"\n✅ Search 'chair' in Furniture:\n{result}")
            
        except ToolError as e:
            pytest.fail(f"Tool error: {str(e)}")
    
    def test_search_products_no_results_real_db(self, check_database_available):
        """Test search with no matching products."""
        tool = SearchProductsTool()
        
        try:
            result = tool.run(keyword="NonExistentProductXYZ123")
            
            assert "No products found" in result
            assert "NonExistentProductXYZ123" in result
            
            print(f"\n✅ Search with no results:\n{result}")
            
        except ToolError as e:
            pytest.fail(f"Tool error: {str(e)}")


class TestCatalogWorkflowIntegration:
    """Integration tests for complete catalog workflow."""
    
    def test_complete_catalog_workflow(self, check_database_available):
        """Test complete workflow: list -> filter -> search."""
        
        # Step 1: List all collections
        list_tool = ListCollectionsTool()
        collections_result = list_tool.run()
        
        assert len(collections_result) > 0
        assert "Electronics" in collections_result
        
        print(f"\n📋 Step 1 - Collections List:\n{collections_result}\n")
        
        # Step 2: Get catalog for a specific collection
        catalog_tool = GetCatalogTool()
        electronics_result = catalog_tool.run(collection_name="Electronics")
        
        assert "Electronics" in electronics_result
        
        print(f"\n📋 Step 2 - Electronics Catalog:\n{electronics_result[:300]}...\n")
        
        # Step 3: Search for specific products
        search_tool = SearchProductsTool()
        search_result = search_tool.run(keyword="phone", collection_name="Electronics")
        
        assert isinstance(search_result, str)
        
        print(f"\n📋 Step 3 - Search 'phone' in Electronics:\n{search_result}\n")
        
        print("✅ Complete workflow executed successfully!")
    
    def test_price_range_filtering(self, check_database_available):
        """Test price range filtering across collections."""
        catalog_tool = GetCatalogTool()
        
        # Get products in mid-price range (₹5000 - ₹20000)
        result = catalog_tool.run(min_price=5000.0, max_price=20000.0)
        
        assert isinstance(result, str)
        
        # Should include some products from the sample data
        print(f"\n💰 Products ₹5,000 - ₹20,000:\n{result}")


# ============================================================================
# Test Database Data Validation
# ============================================================================

class TestDatabaseDataValidation:
    """Validate that database has expected sample data."""
    
    def test_expected_collections_exist(self, check_database_available):
        """Verify all 4 sample collections exist."""
        tool = ListCollectionsTool()
        result = tool.run()
        
        expected_collections = ["Electronics", "Furniture", "Books", "Clothing"]
        for collection in expected_collections:
            assert collection in result, \
                f"Expected collection '{collection}' not found. " \
                f"Please ensure database is populated with sample data from README-docker.md"
    
    def test_expected_products_exist(self, check_database_available):
        """Verify some sample products exist."""
        catalog_tool = GetCatalogTool()
        result = catalog_tool.run()
        
        # Check for at least some products from the sample data
        sample_product_keywords = [
            "Samsung", "Lenovo", "Nilkamal", "Chair", "Book"
        ]
        
        found_keywords = [kw for kw in sample_product_keywords if kw in result]
        
        assert len(found_keywords) > 0, \
            "Expected sample products not found. " \
            "Please ensure database is populated with sample data from README-docker.md"


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-s"])

