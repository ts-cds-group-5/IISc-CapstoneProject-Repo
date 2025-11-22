#!/usr/bin/env python3
"""
Quick test script for shopping cart tools.
Tests tool registration and basic functionality.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def test_cart_tools_registration():
    """Test that all cart tools are registered."""
    print("=" * 70)
    print("SHOPPING CART TOOLS - REGISTRATION TEST")
    print("=" * 70)
    
    try:
        from cccp.tools.registry import get_all_tools
        
        # Get all registered tools
        all_tools = get_all_tools()
        tool_names = [tool.name for tool in all_tools]
        
        print(f"\n✅ Total tools registered: {len(all_tools)}")
        print(f"\n📋 All registered tools:")
        for name in sorted(tool_names):
            print(f"   - {name}")
        
        # Check for cart tools
        print("\n" + "=" * 70)
        print("CART TOOLS CHECK")
        print("=" * 70)
        
        cart_tools = ['addtocart', 'removefromcart', 'viewcart', 'clearcart', 'checkout']
        
        for tool_name in cart_tools:
            if tool_name in tool_names:
                print(f"\n✅ {tool_name} - REGISTERED")
            else:
                print(f"\n❌ {tool_name} - NOT FOUND")
        
        # Summary
        cart_found = sum(1 for name in cart_tools if name in tool_names)
        
        print("\n" + "=" * 70)
        if cart_found == len(cart_tools):
            print(f"✅ SUCCESS: All {len(cart_tools)} cart tools registered!")
            return True
        else:
            print(f"⚠️  WARNING: Only {cart_found}/{len(cart_tools)} cart tools found")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cart_tool_instantiation():
    """Test that cart tools can be instantiated."""
    print("\n" + "=" * 70)
    print("CART TOOL INSTANTIATION TEST")
    print("=" * 70)
    
    try:
        from cccp.tools.order.add_to_cart import AddToCartTool
        from cccp.tools.order.remove_from_cart import RemoveFromCartTool
        from cccp.tools.order.view_cart import ViewCartTool
        from cccp.tools.order.clear_cart import ClearCartTool
        from cccp.tools.order.checkout import CheckoutTool
        
        tools = [
            ("AddToCartTool", AddToCartTool),
            ("RemoveFromCartTool", RemoveFromCartTool),
            ("ViewCartTool", ViewCartTool),
            ("ClearCartTool", ClearCartTool),
            ("CheckoutTool", CheckoutTool)
        ]
        
        for name, tool_class in tools:
            tool = tool_class()
            print(f"\n✅ {name}")
            print(f"   Tool name: {tool.tool_name}")
            print(f"   Description: {tool.description[:60]}...")
            print(f"   Inputs: {tool.inputs}")
        
        print("\n✅ All cart tools instantiated successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cart_utils():
    """Test cart utility functions."""
    print("\n" + "=" * 70)
    print("CART UTILITIES TEST")
    print("=" * 70)
    
    try:
        from cccp.tools.order.cart_utils import (
            get_or_create_cart,
            add_item_to_cart,
            remove_item_from_cart,
            calculate_totals,
            format_cart_display
        )
        
        # Create empty cart
        cart = get_or_create_cart()
        print("\n✅ Created empty cart")
        print(f"   Items: {cart['total_items']}")
        print(f"   Total: ₹{cart['grand_total']}")
        
        # Add a mock product
        mock_product = {
            'product_id': 1,
            'product_name': 'Test Product',
            'product_description': 'Test description',
            'product_price': 999.00,
            'currency': 'INR',
            'product_stock_qty': 10
        }
        
        cart, message = add_item_to_cart(cart, mock_product, 2)
        print(f"\n✅ Added product to cart")
        print(f"   Message: {message}")
        print(f"   Items: {cart['total_items']}")
        print(f"   Total: ₹{cart['grand_total']}")
        
        # Format display
        display = format_cart_display(cart)
        print(f"\n✅ Formatted cart display:")
        print(display[:200] + "...")
        
        print("\n✅ Cart utilities working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🛒 SHOPPING CART TOOLS - VERIFICATION")
    print("=" * 70)
    print("\nThis script verifies shopping cart tools are implemented correctly.\n")
    
    results = {}
    
    # Run tests
    results['registration'] = test_cart_tools_registration()
    results['instantiation'] = test_cart_tool_instantiation()
    results['utilities'] = test_cart_utils()
    
    # Summary
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
        print("\nShopping cart tools are ready to use.")
        print("\nNext steps:")
        print("1. Test with real queries via chat interface")
        print("2. Test complete shopping flow:")
        print("   - Browse catalog")
        print("   - Add items to cart")
        print("   - View cart")
        print("   - Checkout with address")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nPlease review the errors above.")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

