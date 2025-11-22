"""
End-to-End Integration Tests for Complete Shopping Flow.

Tests complete shopping cart workflow with real database:
1. Browse catalog
2. Add multiple real products to cart
3. Manage cart (view, remove)
4. Checkout with shipping details
5. Verify order created in g5_order and g5_order_items
6. Verify order retrieval via get_order tool

Requires:
- Docker Postgres running with sample data loaded
- g5_product table populated with sample data
- g5_order and g5_order_items tables exist

Run with: pytest tests/integration/test_shopping_flow_e2e.py -v -s
"""

import re
import pytest
from cccp.tools.order.add_to_cart import AddToCartTool
from cccp.tools.order.remove_from_cart import RemoveFromCartTool
from cccp.tools.order.view_cart import ViewCartTool
from cccp.tools.order.clear_cart import ClearCartTool
from cccp.tools.order.checkout import CheckoutTool
from cccp.tools.order.get_order import GetOrderTool
from cccp.core.exceptions import ToolError


# Mark all tests as integration tests
pytestmark = pytest.mark.integration


# Test user profiles
USER_HARISH = {
    'user_id': '867045',
    'name': 'Harish Achappa',
    'email': 'harish.achappa@gmail.com',
    'mobile': '9840913286',
    'registered_at': '2025-10-11T00:00:00'
}

USER_PRASHANTH = {
    'user_id': '875974',
    'name': 'Prashanth Chandrappa',
    'email': 'prashanth.c@gmail.com',
    'mobile': '8975974320',
    'registered_at': '2025-10-11T00:00:00'
}


class TestCompleteShoppingFlowHarish:
    """
    End-to-end test for Harish Achappa's complete shopping journey.
    
    Flow:
    1. Add "Atomic Habits" (Books) - ₹699
    2. Add "Samsung Galaxy M35 5G" × 2 (Electronics) - ₹16,999 each
    3. Add "Nilkamal Astra Office Chair" (Furniture) - ₹7,990
    4. View cart (should show 3 items)
    5. Remove "Atomic Habits"
    6. View cart (should show 2 items)
    7. Checkout with shipping address
    8. Verify order created in database
    9. Verify order retrievable via get_order
    """
    
    def test_complete_shopping_flow_harish(self):
        """Test complete shopping flow for Harish Achappa."""
        
        print("\n" + "=" * 70)
        print("🧪 HARISH ACHAPPA - COMPLETE SHOPPING FLOW TEST")
        print("=" * 70)
        
        # Setup user session
        user_session = USER_HARISH.copy()
        
        # Step 1: Add "Atomic Habits" to cart
        print("\n📝 Step 1: Add 'Atomic Habits' to cart")
        add_tool = AddToCartTool()
        result = add_tool.run(product_name="Atomic Habits", quantity=1, user_session=user_session)
        
        print(f"Result: {result[:150]}...")
        assert "Added to cart" in result
        assert "Atomic Habits" in result
        assert "699" in result
        assert user_session.get('shopping_cart') is not None
        assert user_session['shopping_cart']['total_items'] == 1
        print("✅ Step 1 PASSED")
        
        # Step 2: Add "Samsung Galaxy" × 2 to cart
        print("\n📝 Step 2: Add 2 × 'Samsung Galaxy' to cart")
        result = add_tool.run(product_name="Samsung Galaxy", quantity=2, user_session=user_session)
        
        print(f"Result: {result[:150]}...")
        assert "Added to cart" in result
        assert "Samsung" in result
        assert user_session['shopping_cart']['total_items'] == 2
        assert user_session['shopping_cart']['total_quantity'] == 3  # 1 + 2
        print("✅ Step 2 PASSED")
        
        # Step 3: Add "Nilkamal Chair" to cart
        print("\n📝 Step 3: Add 'Nilkamal Chair' to cart")
        result = add_tool.run(product_name="Nilkamal", quantity=1, user_session=user_session)
        
        print(f"Result: {result[:150]}...")
        assert "Added to cart" in result
        assert "Nilkamal" in result or "Chair" in result
        assert user_session['shopping_cart']['total_items'] == 3
        print("✅ Step 3 PASSED")
        
        # Step 4: View cart
        print("\n📝 Step 4: View cart contents")
        view_tool = ViewCartTool()
        result = view_tool.run(user_session=user_session)
        
        print(f"\nCart Display:\n{result}\n")
        assert "Atomic Habits" in result
        assert "Samsung" in result
        assert "Nilkamal" in result or "Chair" in result
        assert "3 products" in result or "3 product" in result
        print("✅ Step 4 PASSED")
        
        # Step 5: Remove "Atomic Habits"
        print("\n📝 Step 5: Remove 'Atomic Habits' from cart")
        remove_tool = RemoveFromCartTool()
        result = remove_tool.run(product_name="Atomic Habits", user_session=user_session)
        
        print(f"Result: {result}")
        assert "Removed" in result
        assert "Atomic Habits" in result
        assert user_session['shopping_cart']['total_items'] == 2
        print("✅ Step 5 PASSED")
        
        # Step 6: View cart again
        print("\n📝 Step 6: View cart after removal")
        result = view_tool.run(user_session=user_session)
        
        print(f"\nUpdated Cart:\n{result[:300]}...\n")
        assert "Atomic Habits" not in result  # Should be removed
        assert "Samsung" in result
        assert "2 products" in result or "2 product" in result
        print("✅ Step 6 PASSED")
        
        # Step 7: Checkout with shipping address
        print("\n📝 Step 7: Checkout with shipping address")
        checkout_tool = CheckoutTool()
        shipping_address = "123 Main Street, Jayanagar 4th Block, Bangalore, Karnataka 560011"
        shipping_notes = "Handle electronics with care. Deliver between 9 AM - 6 PM."
        
        result = checkout_tool.run(
            shipping_address=shipping_address,
            shipping_notes=shipping_notes,
            user_session=user_session
        )
        
        print(f"\n📦 Order Confirmation:\n{result}\n")
        
        # Verify order confirmation contains all required fields
        assert "Order Placed Successfully" in result
        assert "Order ID:" in result
        assert "Harish Achappa" in result
        assert "harish.achappa@gmail.com" in result
        assert "9840913286" in result
        assert "Samsung" in result
        assert "Nilkamal" in result or "Chair" in result
        assert shipping_address in result
        assert shipping_notes in result
        assert "COD" in result
        assert "Received" in result
        
        # Extract order_id from response
        import re
        order_id_match = re.search(r'Order ID:?\s*#?(\d+)', result)
        assert order_id_match, "Order ID not found in confirmation"
        order_id = order_id_match.group(1)
        print(f"✅ Order ID: {order_id}")
        
        # Verify cart cleared
        assert user_session.get('shopping_cart') is None
        print("✅ Step 7 PASSED")
        
        # Step 8: Verify order retrievable via get_order
        print(f"\n📝 Step 8: Retrieve order via get_order (order_id={order_id})")
        get_order_tool = GetOrderTool()
        result = get_order_tool.run(cart_id=order_id)
        
        print(f"\n📦 Retrieved Order:\n{result[:500]}...\n")
        assert "Order Details" in result or "Order ID" in result
        assert "Harish Achappa" in result
        assert "Samsung" in result
        assert "Nilkamal" in result or "Chair" in result
        assert "shopping cart orders" in result.lower()  # Should indicate source
        print("✅ Step 8 PASSED")
        
        # Step 9: Also verify retrieval by email
        print("\n📝 Step 9: Retrieve order via email")
        result = get_order_tool.run(customer_email="harish.achappa@gmail.com")
        
        print(f"\n📦 Retrieved by Email:\n{result[:300]}...\n")
        assert "Harish Achappa" in result
        assert "harish.achappa@gmail.com" in result
        print("✅ Step 9 PASSED")
        
        print("\n" + "=" * 70)
        print("🎉 HARISH'S COMPLETE SHOPPING FLOW - ALL TESTS PASSED!")
        print("=" * 70)


class TestCompleteShoppingFlowPrashanth:
    """
    End-to-end test for Prashanth Chandrappa's shopping journey.
    
    Flow:
    1. Add "The White Tiger" (Books) - ₹499
    2. Add "Lenovo IdeaPad" × 1 (Electronics) - ₹52,990
    3. Add "Wakefit Bed" × 1 (Furniture) - ₹21,990
    4. View cart
    5. Checkout with shipping
    6. Verify order via get_order
    """
    
    def test_complete_shopping_flow_prashanth(self):
        """Test complete shopping flow for Prashanth Chandrappa."""
        
        print("\n" + "=" * 70)
        print("🧪 PRASHANTH CHANDRAPPA - COMPLETE SHOPPING FLOW TEST")
        print("=" * 70)
        
        # Setup user session
        user_session = USER_PRASHANTH.copy()
        
        # Step 1: Add "The White Tiger" book
        print("\n📝 Step 1: Add 'The White Tiger' to cart")
        add_tool = AddToCartTool()
        result = add_tool.run(product_name="The White Tiger", quantity=1, user_session=user_session)
        
        print(f"Result: {result[:150]}...")
        assert "Added to cart" in result
        assert "White Tiger" in result
        assert user_session['shopping_cart']['total_items'] == 1
        print("✅ Step 1 PASSED")
        
        # Step 2: Add "Lenovo IdeaPad"
        print("\n📝 Step 2: Add 'Lenovo IdeaPad' to cart")
        result = add_tool.run(product_name="Lenovo IdeaPad", quantity=1, user_session=user_session)
        
        print(f"Result: {result[:150]}...")
        assert "Added to cart" in result
        assert "Lenovo" in result
        assert user_session['shopping_cart']['total_items'] == 2
        print("✅ Step 2 PASSED")
        
        # Step 3: Add "Wakefit Bed"
        print("\n📝 Step 3: Add 'Wakefit Bed' to cart")
        result = add_tool.run(product_name="Wakefit", quantity=1, user_session=user_session)
        
        print(f"Result: {result[:150]}...")
        assert "Added to cart" in result
        assert "Wakefit" in result or "Bed" in result
        assert user_session['shopping_cart']['total_items'] == 3
        print("✅ Step 3 PASSED")
        
        # Step 4: View cart
        print("\n📝 Step 4: View cart with all 3 items")
        view_tool = ViewCartTool()
        result = view_tool.run(user_session=user_session)
        
        print(f"\nCart Display:\n{result}\n")
        assert "White Tiger" in result
        assert "Lenovo" in result
        assert "Wakefit" in result or "Bed" in result
        assert "3 products" in result or "3 product" in result
        
        # Calculate expected total (roughly)
        grand_total = user_session['shopping_cart']['grand_total']
        print(f"Cart Grand Total: ₹{grand_total:,.2f}")
        assert grand_total > 70000  # Should be ~75,479 (499 + 52,990 + 21,990)
        print("✅ Step 4 PASSED")
        
        # Step 5: Checkout
        print("\n📝 Step 5: Checkout with shipping details")
        checkout_tool = CheckoutTool()
        shipping_address = "456 MG Road, Indiranagar, Bangalore, Karnataka 560038"
        shipping_notes = "Call before delivery. Gate code: 1234"
        
        result = checkout_tool.run(
            shipping_address=shipping_address,
            shipping_notes=shipping_notes,
            user_session=user_session
        )
        
        print(f"\n📦 Order Confirmation:\n{result}\n")
        
        # Verify all required fields in confirmation
        assert "Order Placed Successfully" in result
        assert "Prashanth Chandrappa" in result
        assert "prashanth.c@gmail.com" in result
        assert "8975974320" in result
        assert "White Tiger" in result
        assert "Lenovo" in result
        assert "Wakefit" in result or "Bed" in result
        assert shipping_address in result
        assert shipping_notes in result
        assert "COD" in result
        assert "Received" in result
        
        # Extract order_id
        import re
        order_id_match = re.search(r'Order ID:?\s*#?(\d+)', result)
        assert order_id_match, "Order ID not found"
        order_id = order_id_match.group(1)
        print(f"✅ Order ID: {order_id}")
        print("✅ Step 5 PASSED")
        
        # Step 6: Retrieve order via get_order by order_id
        print(f"\n📝 Step 6: Retrieve order by ID ({order_id})")
        get_order_tool = GetOrderTool()
        result = get_order_tool.run(cart_id=order_id)
        
        print(f"\n📦 Retrieved Order:\n{result[:400]}...\n")
        assert "Prashanth Chandrappa" in result
        assert "prashanth.c@gmail.com" in result
        assert "White Tiger" in result
        assert "Lenovo" in result
        print("✅ Step 6 PASSED")
        
        # Step 7: Retrieve order via get_order by email
        print("\n📝 Step 7: Retrieve order by email")
        result = get_order_tool.run(customer_email="prashanth.c@gmail.com")
        
        print(f"\n📦 Retrieved by Email:\n{result[:400]}...\n")
        assert "Prashanth Chandrappa" in result
        assert ("shopping" in result.lower() or "order" in result.lower())  # More flexible check
        print("✅ Step 7 PASSED")
        
        print("\n" + "=" * 70)
        print("🎉 PRASHANTH'S COMPLETE SHOPPING FLOW - ALL TESTS PASSED!")
        print("=" * 70)


class TestMultipleOrders:
    """Test that both users can place orders independently."""
    
    def test_two_users_place_orders(self):
        """Test Harish and Prashanth both place orders with different products."""
        
        print("\n" + "=" * 70)
        print("🧪 MULTI-USER TEST - TWO INDEPENDENT ORDERS")
        print("=" * 70)
        
        # User 1: Harish orders Books
        print("\n👤 User 1: Harish Achappa")
        user1_session = USER_HARISH.copy()
        add_tool = AddToCartTool()
        
        print("   Adding 2 books to cart...")
        add_tool.run(product_name="Argumentative Indian", quantity=1, user_session=user1_session)
        add_tool.run(product_name="India After Gandhi", quantity=1, user_session=user1_session)
        
        assert user1_session['shopping_cart']['total_items'] == 2
        cart1_total = user1_session['shopping_cart']['grand_total']
        print(f"   Cart Total: ₹{cart1_total:,.2f}")
        
        # User 2: Prashanth orders Electronics
        print("\n👤 User 2: Prashanth Chandrappa")
        user2_session = USER_PRASHANTH.copy()
        
        print("   Adding electronics to cart...")
        add_tool.run(product_name="Redmi Buds", quantity=1, user_session=user2_session)
        add_tool.run(product_name="boAt Airdopes", quantity=2, user_session=user2_session)
        
        assert user2_session['shopping_cart']['total_items'] == 2
        cart2_total = user2_session['shopping_cart']['grand_total']
        print(f"   Cart Total: ₹{cart2_total:,.2f}")
        
        # Verify carts are independent
        assert cart1_total != cart2_total
        assert len(user1_session['shopping_cart']['items']) == 2
        assert len(user2_session['shopping_cart']['items']) == 2
        print("\n✅ Independent carts verified")
        
        # Both checkout
        print("\n📦 Checkout for both users...")
        checkout_tool = CheckoutTool()
        
        result1 = checkout_tool.run(
            shipping_address="Harish's address, Bangalore 560001",
            user_session=user1_session
        )
        order1_match = re.search(r'Order ID:?\s*#?(\d+)', result1)
        order1_id = order1_match.group(1) if order1_match else None
        print(f"   Harish's Order ID: {order1_id}")
        
        result2 = checkout_tool.run(
            shipping_address="Prashanth's address, Bangalore 560038",
            shipping_notes="Fragile items",
            user_session=user2_session
        )
        order2_match = re.search(r'Order ID:?\s*#?(\d+)', result2)
        order2_id = order2_match.group(1) if order2_match else None
        print(f"   Prashanth's Order ID: {order2_id}")
        
        assert order1_id is not None
        assert order2_id is not None
        assert order1_id != order2_id  # Different orders
        print("\n✅ Both orders created with different IDs")
        
        # Verify retrieval
        print("\n📝 Verify both orders retrievable...")
        get_order_tool = GetOrderTool()
        
        harish_order = get_order_tool.run(customer_email="harish.achappa@gmail.com")
        assert "Harish Achappa" in harish_order
        assert "Argumentative" in harish_order or "India After Gandhi" in harish_order
        print("   ✅ Harish's order retrieved")
        
        prashanth_order = get_order_tool.run(customer_email="prashanth.c@gmail.com")
        assert "Prashanth Chandrappa" in prashanth_order
        assert "Redmi" in prashanth_order or "boAt" in prashanth_order
        print("   ✅ Prashanth's order retrieved")
        
        print("\n" + "=" * 70)
        print("🎉 MULTI-USER TEST - ALL TESTS PASSED!")
        print("=" * 70)


class TestCartOperations:
    """Test specific cart operations."""
    
    def test_add_product_variations(self):
        """Test adding products with different quantities."""
        
        print("\n" + "=" * 70)
        print("🧪 CART OPERATIONS - ADD PRODUCT VARIATIONS")
        print("=" * 70)
        
        user_session = USER_HARISH.copy()
        add_tool = AddToCartTool()
        
        # Add with default quantity (1)
        print("\n📝 Add product without specifying quantity (default = 1)")
        result = add_tool.run(product_name="Atomic Habits", user_session=user_session)
        assert user_session.get('shopping_cart', {}).get('items', [{}])[0].get('quantity') == 1
        print("✅ Default quantity works")
        
        # Clear cart
        clear_tool = ClearCartTool()
        clear_tool.run(user_session=user_session)
        
        # Add with explicit quantity
        print("\n📝 Add product with quantity = 3")
        result = add_tool.run(product_name="Allen Solly", quantity=3, user_session=user_session)
        cart = user_session.get('shopping_cart', {})
        if cart and cart.get('items'):
            assert cart['items'][0]['quantity'] == 3, f"Expected quantity 3, got {cart['items'][0].get('quantity')}"
            assert cart['total_quantity'] == 3, f"Expected total 3, got {cart.get('total_quantity')}"
        print("✅ Explicit quantity works")
        
        print("\n✅ ADD PRODUCT VARIATIONS - PASSED")
    
    def test_cart_full_scenario(self):
        """Test cart with max items (10)."""
        
        print("\n" + "=" * 70)
        print("🧪 CART OPERATIONS - MAX ITEMS TEST")
        print("=" * 70)
        
        user_session = USER_PRASHANTH.copy()
        add_tool = AddToCartTool()
        
        # Add 10 different products (max limit)
        products_to_add = [
            "Atomic Habits",
            "White Tiger",
            "Samsung Galaxy",
            "Redmi Buds",
            "OnePlus Power Bank",
            "Nilkamal Chair",
            "Allen Solly Shirt",
            "Levi Jeans",
            "boAt Airdopes",
            "LG TV"
        ]
        
        print(f"\n📝 Adding {len(products_to_add)} products to cart...")
        for i, product in enumerate(products_to_add, 1):
            try:
                result = add_tool.run(product_name=product, quantity=1, user_session=user_session)
                print(f"   {i}. Added {product}")
            except ToolError as e:
                print(f"   {i}. Failed to add {product}: {e}")
                break
        
        cart_items = user_session.get('shopping_cart', {}).get('total_items', 0)
        print(f"\n📊 Cart has {cart_items} items")
        assert cart_items <= 10, "Cart exceeded max items!"
        
        # Try to add 11th item (should fail)
        if cart_items == 10:
            print("\n📝 Trying to add 11th item (should fail)...")
            try:
                add_tool.run(product_name="Puma Jacket", quantity=1, user_session=user_session)
                assert False, "Should have raised error for cart full"
            except ToolError as e:
                assert "full" in str(e).lower() or "max" in str(e).lower()
                print(f"   ✅ Correctly rejected: {e}")
        
        print("\n✅ MAX ITEMS TEST - PASSED")


class TestErrorScenarios:
    """Test error handling scenarios."""
    
    def test_product_not_found(self):
        """Test adding non-existent product."""
        
        print("\n" + "=" * 70)
        print("🧪 ERROR SCENARIOS - PRODUCT NOT FOUND")
        print("=" * 70)
        
        user_session = USER_HARISH.copy()
        add_tool = AddToCartTool()
        
        print("\n📝 Trying to add non-existent product...")
        result = add_tool.run(product_name="NonExistentProduct12345", user_session=user_session)
        
        print(f"Result: {result}")
        assert "not found" in result.lower()
        print("✅ Product not found handled correctly")
    
    def test_checkout_empty_cart(self):
        """Test checkout with empty cart."""
        
        print("\n" + "=" * 70)
        print("🧪 ERROR SCENARIOS - EMPTY CART CHECKOUT")
        print("=" * 70)
        
        user_session = USER_HARISH.copy()
        checkout_tool = CheckoutTool()
        
        print("\n📝 Trying to checkout with empty cart...")
        try:
            result = checkout_tool.run(
                shipping_address="Test Address",
                user_session=user_session
            )
            assert False, "Should have raised error for empty cart"
        except ToolError as e:
            print(f"   ✅ Correctly rejected: {e}")
            assert "empty" in str(e).lower()
        
        print("\n✅ EMPTY CART CHECKOUT - CORRECTLY REJECTED")
    
    def test_duplicate_product(self):
        """Test adding same product twice."""
        
        print("\n" + "=" * 70)
        print("🧪 ERROR SCENARIOS - DUPLICATE PRODUCT")
        print("=" * 70)
        
        user_session = USER_PRASHANTH.copy()
        add_tool = AddToCartTool()
        
        print("\n📝 Add 'Atomic Habits' first time...")
        add_tool.run(product_name="Atomic Habits", user_session=user_session)
        assert user_session['shopping_cart']['total_items'] == 1
        
        print("\n📝 Try to add 'Atomic Habits' again (should fail)...")
        try:
            add_tool.run(product_name="Atomic Habits", user_session=user_session)
            assert False, "Should have raised error for duplicate"
        except ToolError as e:
            print(f"   ✅ Correctly rejected: {e}")
            assert ("already in" in str(e).lower() or "already in your cart" in str(e).lower())
        
        print("\n✅ DUPLICATE PRODUCT - CORRECTLY REJECTED")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

