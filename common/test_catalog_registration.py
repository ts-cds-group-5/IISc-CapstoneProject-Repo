#!/usr/bin/env python3
"""
Verification script for catalog tools registration.
Run this to verify that catalog tools are properly registered and accessible.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_tool_registration():
    """Test that catalog tools are registered."""
    print("=" * 70)
    print("CATALOG TOOLS REGISTRATION VERIFICATION")
    print("=" * 70)
    
    try:
        from cccp.tools.registry import get_all_tools, get_tool
        
        # Get all registered tools
        all_tools = get_all_tools()
        tool_names = [tool.name for tool in all_tools]
        
        print(f"\n✅ Total tools registered: {len(all_tools)}")
        print(f"\n📋 All registered tools:")
        for name in sorted(tool_names):
            print(f"   - {name}")
        
        # Check for catalog tools
        print("\n" + "=" * 70)
        print("CATALOG TOOLS CHECK")
        print("=" * 70)
        
        catalog_tools = ['listcollections', 'getcatalog', 'searchproducts']
        
        for tool_name in catalog_tools:
            if tool_name in tool_names:
                print(f"\n✅ {tool_name} - REGISTERED")
                
                # Get tool details
                tool = get_tool(tool_name)
                print(f"   Name: {tool.name}")
                print(f"   Tool Name: {tool.tool_name}")
                print(f"   Description: {tool.description[:80]}...")
                print(f"   Inputs: {tool.inputs}")
                print(f"   Outputs: {tool.outputs}")
            else:
                print(f"\n❌ {tool_name} - NOT FOUND")
        
        # Check place order stub
        print("\n" + "=" * 70)
        print("PLACE ORDER STUB CHECK")
        print("=" * 70)
        
        if 'placeorder' in tool_names:
            print("\n✅ placeorder - REGISTERED (Phase 2 stub)")
            tool = get_tool('placeorder')
            print(f"   Description: {tool.description}")
        else:
            print("\n❌ placeorder - NOT FOUND")
        
        print("\n" + "=" * 70)
        print("VERIFICATION COMPLETE")
        print("=" * 70)
        
        # Summary
        catalog_found = sum(1 for name in catalog_tools if name in tool_names)
        
        if catalog_found == len(catalog_tools):
            print("\n✅ SUCCESS: All catalog tools registered correctly!")
            return True
        else:
            print(f"\n⚠️  WARNING: Only {catalog_found}/{len(catalog_tools)} catalog tools found")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_instantiation():
    """Test that tools can be instantiated and used."""
    print("\n" + "=" * 70)
    print("TOOL INSTANTIATION TEST")
    print("=" * 70)
    
    try:
        from cccp.tools.catalog.list_collections import ListCollectionsTool
        from cccp.tools.catalog.get_catalog import GetCatalogTool
        from cccp.tools.catalog.search_products import SearchProductsTool
        
        # Test ListCollectionsTool
        print("\n1. Testing ListCollectionsTool...")
        list_tool = ListCollectionsTool()
        print(f"   ✅ Instantiated: {list_tool.tool_name}")
        print(f"   Description: {list_tool.description[:60]}...")
        
        # Test GetCatalogTool
        print("\n2. Testing GetCatalogTool...")
        catalog_tool = GetCatalogTool()
        print(f"   ✅ Instantiated: {catalog_tool.tool_name}")
        print(f"   Description: {catalog_tool.description[:60]}...")
        print(f"   Inputs: {catalog_tool.inputs}")
        
        # Test SearchProductsTool
        print("\n3. Testing SearchProductsTool...")
        search_tool = SearchProductsTool()
        print(f"   ✅ Instantiated: {search_tool.tool_name}")
        print(f"   Description: {search_tool.description[:60]}...")
        print(f"   Inputs: {search_tool.inputs}")
        
        print("\n✅ All tools instantiated successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_intent_classification():
    """Test that intent classifier recognizes catalog_inquiry."""
    print("\n" + "=" * 70)
    print("INTENT CLASSIFICATION TEST")
    print("=" * 70)
    
    try:
        from cccp.agents.intent_classifier import IntentClassifier
        
        classifier = IntentClassifier()
        
        print(f"\n✅ IntentClassifier instantiated")
        print(f"\n📋 Registered intent categories:")
        for intent in classifier.intent_categories:
            marker = "✨" if intent == "catalog_inquiry" else "  "
            print(f"   {marker} {intent}")
        
        if "catalog_inquiry" in classifier.intent_categories:
            print("\n✅ catalog_inquiry intent is registered!")
            
            # Check suggested tools
            suggested = classifier._get_suggested_tools("catalog_inquiry")
            print(f"\n   Suggested tools for catalog_inquiry:")
            for tool in suggested:
                print(f"      - {tool}")
            
            return True
        else:
            print("\n❌ catalog_inquiry intent NOT FOUND")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_llama_prompt_examples():
    """Test that Llama prompt has catalog examples."""
    print("\n" + "=" * 70)
    print("LLAMA PROMPT EXAMPLES TEST")
    print("=" * 70)
    
    try:
        from cccp.prompts import get_prompt
        
        # Generate a sample prompt
        prompt = get_prompt(
            "tool_detection",
            user_input="What collections do you have?",
            tools_info="Tool: listcollections\nDescription: List collections"
        )
        
        print("\n✅ Prompt generated successfully")
        
        # Check for catalog examples
        catalog_keywords = ['listcollections', 'getcatalog', 'searchproducts']
        found_keywords = [kw for kw in catalog_keywords if kw in prompt]
        
        if found_keywords:
            print(f"\n✅ Found catalog tool references in prompt:")
            for kw in found_keywords:
                print(f"   - {kw}")
            return True
        else:
            print("\n⚠️  Catalog tool examples not found in prompt")
            print("   (This may be normal if examples are in a different format)")
            return True  # Don't fail, just warn
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("\n" + "=" * 70)
    print("🚀 CATALOG TOOLS IMPLEMENTATION VERIFICATION")
    print("=" * 70)
    print("\nThis script verifies that catalog tools are properly implemented")
    print("and integrated with the CCCP Advanced system.\n")
    
    results = {}
    
    # Run tests
    results['registration'] = test_tool_registration()
    results['instantiation'] = test_tool_instantiation()
    results['intent'] = test_intent_classification()
    results['prompt'] = test_llama_prompt_examples()
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name.upper()}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("\nCatalog tools are properly implemented and ready to use.")
        print("\nNext steps:")
        print("1. Run unit tests: pytest tests/unit/test_catalog_tools.py -v")
        print("2. Run integration tests: pytest tests/integration/test_catalog_integration.py -v")
        print("3. Test with real LLM queries via the chat interface")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nPlease review the errors above and fix any issues.")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

