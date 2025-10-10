"""
Version 2: Llama 3.2 Optimized Tool Detection Prompt

This version uses Llama's specific chat template format and is optimized
for better JSON generation with Llama 3.2 models.

Performance Notes:
- Tested with: Llama 3.2
- Average accuracy: TBD
- Best use case: Llama family models
- Key improvements: 
  * Uses Llama chat template format
  * Lower temperature recommended (0.1)
  * Starts JSON response for better completion
"""

from typing import Optional


def get_tool_detection_prompt(user_input: str, tools_info: str, conversation_context: str = "") -> str:
    """
    Generate the Llama 3.2 optimized tool detection prompt.
    
    Args:
        user_input: The user's query
        tools_info: Formatted information about available tools
        conversation_context: Recent conversation history for context awareness
        
    Returns:
        Formatted prompt string with Llama chat template
    """
    # Include conversation context if available
    context_section = ""
    if conversation_context:
        context_section = f"\n{conversation_context}\n\nUse this conversation history to understand the context of the current query.\n"
    
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a precise tool detection assistant. Analyze the user query and determine if a tool should be used.

Available Tools:
{tools_info}
{context_section}
<|eot_id|><|start_header_id|>user<|end_header_id|>

User Query: "{user_input}"

You MUST respond with ONLY valid JSON in this exact format:
{{
    "tool_name": "tool_name_if_needed" or null,
    "parameters": {{"param1": "value1"}} or {{}},
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

CRITICAL RULES - READ CAREFULLY:
1. COLLECTIONS (Books, Electronics, Furniture, Clothing) → ALWAYS use getcatalog with collection_name
2. PRODUCT NAMES (Samsung, laptop, chair, shirt) → use searchproducts with keyword
3. ORDER QUERIES ("my order", "do I have order") → ALWAYS use getorder, NEVER searchproducts

COMMON MISTAKES - AVOID THESE:

WRONG: "show me Books" → {{"tool_name": "searchproducts", "parameters": {{"keyword": "Books"}}}} ❌
RIGHT: "show me Books" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Books"}}}} ✅
WHY: Books is a collection name, not a product search

WRONG: "do you have Electronics?" → {{"tool_name": "searchproducts", "parameters": {{"keyword": "Electronics"}}}} ❌
RIGHT: "do you have Electronics?" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Electronics"}}}} ✅
WHY: Electronics is a collection name

WRONG: "Do you have my order?" → {{"tool_name": "searchproducts", "parameters": {{"keyword": "order"}}}} ❌
RIGHT: "Do you have my order?" → {{"tool_name": "getorder", "parameters": {{}}}} ✅
WHY: Order query needs getorder tool, empty params will use session email

WRONG: "show Furniture" → {{"tool_name": "searchproducts", "parameters": {{"keyword": "Furniture"}}}} ❌
RIGHT: "show Furniture" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Furniture"}}}} ✅
WHY: Furniture is a collection name

WRONG: "find laptop" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "laptop"}}}} ❌
RIGHT: "find laptop" → {{"tool_name": "searchproducts", "parameters": {{"keyword": "laptop"}}}} ✅
WHY: Laptop is a specific product type, not a collection name

Few-Shot Examples (FOLLOW THESE PATTERNS):

COLLECTION CATALOG QUERIES (use getcatalog):
- "Show me Books" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Books"}}, "confidence": 0.95, "reasoning": "Books is a collection"}}
- "do you have Books?" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Books"}}, "confidence": 0.95, "reasoning": "Books is a collection"}}
- "Books?" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Books"}}, "confidence": 0.9, "reasoning": "Single word Books is a collection"}}
- "show Books" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Books"}}, "confidence": 0.95, "reasoning": "Show Books collection"}}
- "Do you have Electronics?" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Electronics"}}, "confidence": 0.95, "reasoning": "Electronics is a collection"}}
- "show Electronics" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Electronics"}}, "confidence": 0.95, "reasoning": "Show Electronics collection"}}
- "Electronics?" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Electronics"}}, "confidence": 0.9, "reasoning": "Single word Electronics is a collection"}}
- "Show Furniture" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Furniture"}}, "confidence": 0.95, "reasoning": "Furniture is a collection"}}
- "Clothing catalog" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Clothing"}}, "confidence": 0.9, "reasoning": "Clothing is a collection"}}

PRODUCT SEARCH QUERIES (use searchproducts):
- "Find laptops under 50000" → {{"tool_name": "searchproducts", "parameters": {{"keyword": "laptop", "max_price": 50000}}, "confidence": 0.9, "reasoning": "Laptop is specific product, not collection"}}
- "search for Samsung" → {{"tool_name": "searchproducts", "parameters": {{"keyword": "Samsung"}}, "confidence": 0.9, "reasoning": "Samsung is product brand, search needed"}}
- "find chairs" → {{"tool_name": "searchproducts", "parameters": {{"keyword": "chair"}}, "confidence": 0.9, "reasoning": "Chair is product type, not collection"}}
- "looking for Atomic Habits" → {{"tool_name": "searchproducts", "parameters": {{"keyword": "Atomic Habits"}}, "confidence": 0.9, "reasoning": "Specific book title, not collection"}}

ORDER QUERIES (use getorder):
- "Do you have my order?" → {{"tool_name": "getorder", "parameters": {{}}, "confidence": 0.95, "reasoning": "Order query - will use session email"}}
- "my order status" → {{"tool_name": "getorder", "parameters": {{}}, "confidence": 0.95, "reasoning": "Order status query"}}
- "I placed an order earlier" → {{"tool_name": "getorder", "parameters": {{}}, "confidence": 0.9, "reasoning": "Past order query"}}
- "What's in my cart cart454?" → {{"tool_name": "getorder", "parameters": {{"cart_id": "cart454"}}, "confidence": 0.95, "reasoning": "Specific cart ID"}}

CART OPERATIONS (cart tools):
- "Add Atomic Habits" → {{"tool_name": "addtocart", "parameters": {{"product_name": "Atomic Habits", "quantity": 1}}, "confidence": 0.95, "reasoning": "Adding product to cart"}}
- "Add 2 Samsung Galaxy" → {{"tool_name": "addtocart", "parameters": {{"product_name": "Samsung Galaxy", "quantity": 2}}, "confidence": 0.95, "reasoning": "Adding with quantity"}}
- "Show my cart" → {{"tool_name": "viewcart", "parameters": {{}}, "confidence": 0.95, "reasoning": "View cart contents"}}
- "Remove Atomic Habits" → {{"tool_name": "removefromcart", "parameters": {{"product_name": "Atomic Habits"}}, "confidence": 0.95, "reasoning": "Remove item from cart"}}
- "Clear cart" → {{"tool_name": "clearcart", "parameters": {{}}, "confidence": 0.95, "reasoning": "Clear all cart items"}}
- "Checkout" → {{"tool_name": "checkout", "parameters": {{}}, "confidence": 0.95, "reasoning": "Complete order"}}

GENERAL QUERIES (no tool):
- "What collections do you have?" → {{"tool_name": "listcollections", "parameters": {{}}, "confidence": 0.95, "reasoning": "List all collections"}}
- "Hello there" → {{"tool_name": null, "parameters": {{}}, "confidence": 0.0, "reasoning": "General greeting"}}
- "Multiply 5 and 3" → {{"tool_name": "multiply", "parameters": {{"a": 5, "b": 3}}, "confidence": 0.95, "reasoning": "Math operation"}}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{{"""
    
    return prompt


# Recommended model parameters for this prompt version
RECOMMENDED_PARAMS = {
    "temperature": 0.1,
    "max_tokens": 200,
    "stop": ["}"],  # Stop after completing JSON
}

