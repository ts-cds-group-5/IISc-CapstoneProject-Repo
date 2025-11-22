"""
Version 3: Enhanced Tool Detection Prompt (Experimental)

This version is for testing new approaches and improvements.
Use this for experimentation before promoting to a stable version.

Performance Notes:
- Tested with: TBD
- Average accuracy: TBD
- Best use case: Experimentation
- Key features: Add your experimental features here
"""

from typing import Optional


def get_tool_detection_prompt(user_input: str, tools_info: str) -> str:
    """
    Generate an enhanced/experimental tool detection prompt.
    
    Args:
        user_input: The user's query
        tools_info: Formatted information about available tools
        
    Returns:
        Formatted prompt string
        
    Note:
        This is an experimental version. Modify as needed for testing.
    """
    # TODO: Implement your experimental prompt here
    # For now, use v2 as base
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
- "Hello there" → {{"tool_name": null, "parameters": {{}}, "confidence": 0.0, "reasoning": "General greeting"}}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{{"""
    
    return prompt

