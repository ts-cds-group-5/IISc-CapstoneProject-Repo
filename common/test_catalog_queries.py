#!/usr/bin/env python3
"""
Quick test script for catalog tools with real database.
Tests the positional parameter fix and common query patterns.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_parameter_building():
    """Test parameter building with positional parameters."""
    print("=" * 70)
    print("TEST 1: Parameter Building")
    print("=" * 70)
    
    from cccp.tools.catalog.catalog_utils import build_filter_where_clauses
    
    # Test 1: Single collection filter
    filters = {'collection_name': 'Books', 'in_stock_only': True}
    where_clauses, params = build_filter_where_clauses(filters)
    
    print(f"\n✅ Test 1: Collection filter")
    print(f"   Filters: {filters}")
    print(f"   WHERE clauses: {where_clauses}")
    print(f"   Params: {params}")
    
    assert "c.name = $1" in where_clauses[1], "Should use positional parameter $1"
    assert params.get('1') == 'Books', "Param should have numeric string key"
    print("   ✅ PASS: Positional parameters correct")
    
    # Test 2: Multiple filters
    filters = {
        'collection_name': 'Electronics',
        'max_price': 10000.0,
        'in_stock_only': True
    }
    where_clauses, params = build_filter_where_clauses(filters)
    
    print(f"\n✅ Test 2: Multiple filters")
    print(f"   Filters: {filters}")
    print(f"   WHERE clauses: {where_clauses}")
    print(f"   Params: {params}")
    
    assert params.get('1') == 'Electronics', "First param should be collection"
    assert params.get('2') == 10000.0, "Second param should be price"
    print("   ✅ PASS: Parameter order correct")
    
    return True


def test_list_collections():
    """Test list collections tool."""
    print("\n" + "=" * 70)
    print("TEST 2: List Collections Tool")
    print("=" * 70)
    
    from cccp.tools.catalog.list_collections import ListCollectionsTool
    
    tool = ListCollectionsTool()
    
    try:
        print("\n🔄 Fetching collections from database...")
        result = tool.run()
        
        print(f"\n✅ SUCCESS:")
        print(result)
        
        # Verify expected collections
        for collection in ['Electronics', 'Furniture', 'Books', 'Clothing']:
            if collection in result:
                print(f"   ✅ Found: {collection}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_get_catalog_with_filter():
    """Test get catalog with collection filter (tests positional params)."""
    print("\n" + "=" * 70)
    print("TEST 3: Get Catalog with Filter (Positional Params)")
    print("=" * 70)
    
    from cccp.tools.catalog.get_catalog import GetCatalogTool
    
    tool = GetCatalogTool()
    
    try:
        print("\n🔄 Fetching Books catalog...")
        result = tool.run(collection_name="Books")
        
        print(f"\n✅ SUCCESS:")
        print(result[:500] + "...")  # Truncate for readability
        
        assert "Books" in result, "Should show Books collection"
        print("\n   ✅ Positional parameters working correctly!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_get_catalog_with_price_filter():
    """Test get catalog with price filter."""
    print("\n" + "=" * 70)
    print("TEST 4: Get Catalog with Price Filter")
    print("=" * 70)
    
    from cccp.tools.catalog.get_catalog import GetCatalogTool
    
    tool = GetCatalogTool()
    
    try:
        print("\n🔄 Fetching products under ₹10,000...")
        result = tool.run(max_price=10000.0)
        
        print(f"\n✅ SUCCESS:")
        print(result[:500] + "...")  # Truncate for readability
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_search_products():
    """Test search products tool."""
    print("\n" + "=" * 70)
    print("TEST 5: Search Products")
    print("=" * 70)
    
    from cccp.tools.catalog.search_products import SearchProductsTool
    
    tool = SearchProductsTool()
    
    try:
        print("\n🔄 Searching for 'book'...")
        result = tool.run(keyword="book")
        
        print(f"\n✅ SUCCESS:")
        print(result[:500] + "...")  # Truncate for readability
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_combined_filters():
    """Test catalog with multiple combined filters."""
    print("\n" + "=" * 70)
    print("TEST 6: Combined Filters (Collection + Price)")
    print("=" * 70)
    
    from cccp.tools.catalog.get_catalog import GetCatalogTool
    
    tool = GetCatalogTool()
    
    try:
        print("\n🔄 Fetching Electronics under ₹20,000...")
        result = tool.run(collection_name="Electronics", max_price=20000.0)
        
        print(f"\n✅ SUCCESS:")
        print(result[:500] + "...")  # Truncate for readability
        
        assert "Electronics" in result or "No products found" in result
        print("\n   ✅ Multiple positional parameters working correctly!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🧪 CATALOG TOOLS - QUICK TEST SUITE")
    print("=" * 70)
    print("\nThis script tests catalog tools with real database.")
    print("Ensure Docker Postgres is running with sample data loaded.\n")
    
    results = {}
    
    # Run tests
    results['parameter_building'] = test_parameter_building()
    results['list_collections'] = test_list_collections()
    results['get_catalog_filter'] = test_get_catalog_with_filter()
    results['price_filter'] = test_get_catalog_with_price_filter()
    results['search_products'] = test_search_products()
    results['combined_filters'] = test_combined_filters()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nCatalog tools are working correctly with database.")
        print("Positional parameters are properly handled.")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nCheck the errors above for details.")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

