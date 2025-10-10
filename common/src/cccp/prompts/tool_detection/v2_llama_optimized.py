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


def get_tool_detection_prompt(user_input: str, tools_info: str) -> str:
    """
    Generate the Llama 3.2 optimized tool detection prompt.
    
    Args:
        user_input: The user's query
        tools_info: Formatted information about available tools
        
    Returns:
        Formatted prompt string with Llama chat template
    """
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a precise tool detection assistant. Analyze the user query and determine if a tool should be used.

Available Tools:
{tools_info}

<|eot_id|><|start_header_id|>user<|end_header_id|>

User Query: "{user_input}"

You MUST respond with ONLY valid JSON in this exact format:
{{
    "tool_name": "tool_name_if_needed" or null,
    "parameters": {{"param1": "value1"}} or {{}},
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Examples:
- "What's in my cart cart454?" → {{"tool_name": "getorder", "parameters": {{"cart_id": "cart454"}}, "confidence": 0.9, "reasoning": "User asking about specific cart"}}
- "What happened to my order 2?" → {{"tool_name": "getorder", "parameters": {{"cart_id": "2"}}, "confidence": 0.85, "reasoning": "User asking about order/cart 2"}}
- "What collections do you have?" → {{"tool_name": "listcollections", "parameters": {{}}, "confidence": 0.95, "reasoning": "User asking for collections list"}}
- "Show me Electronics catalog" → {{"tool_name": "getcatalog", "parameters": {{"collection_name": "Electronics"}}, "confidence": 0.9, "reasoning": "User wants Electronics products"}}
- "Find laptops under 50000" → {{"tool_name": "searchproducts", "parameters": {{"keyword": "laptop", "max_price": 50000}}, "confidence": 0.9, "reasoning": "User searching with keyword and price"}}
- "Add 2 Samsung Galaxy" → {{"tool_name": "addtocart", "parameters": {{"product_name": "Samsung Galaxy", "quantity": 2}}, "confidence": 0.9, "reasoning": "User adding product to cart"}}
- "Show my cart" → {{"tool_name": "viewcart", "parameters": {{}}, "confidence": 0.95, "reasoning": "User wants to view cart"}}
- "Checkout" → {{"tool_name": "checkout", "parameters": {{}}, "confidence": 0.95, "reasoning": "User wants to complete order"}}
- "Hello there" → {{"tool_name": null, "parameters": {{}}, "confidence": 0.0, "reasoning": "General greeting"}}
- "Multiply 5 and 3" → {{"tool_name": "multiply", "parameters": {{"a": 5, "b": 3}}, "confidence": 0.95, "reasoning": "Clear math operation"}}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{{"""
    
    return prompt


# Recommended model parameters for this prompt version
RECOMMENDED_PARAMS = {
    "temperature": 0.1,
    "max_tokens": 200,
    "stop": ["}"],  # Stop after completing JSON
}

