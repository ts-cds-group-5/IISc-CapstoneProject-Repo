"""
Version 1: Basic LLM Tool Detection Prompt

This is the baseline prompt for tool detection.
Works well with general-purpose LLMs like GPT-3.5/4.

Performance Notes:
- Tested with: General purpose models
- Average accuracy: TBD
- Best use case: Standard LLMs with good JSON generation
"""

from typing import Optional


def get_tool_detection_prompt(user_input: str, tools_info: str) -> str:
    """
    Generate the basic tool detection prompt.
    
    Args:
        user_input: The user's query
        tools_info: Formatted information about available tools
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""You are a tool detection assistant. Given a user query, determine if a specific tool should be used and extract parameters.

Available Tools:
{tools_info}

User Query: "{user_input}"

IMPORTANT: You must respond with ONLY valid JSON. No additional text, explanations, or formatting.

Required JSON format:
{{
    "tool_name": "tool_name_if_needed" or null,
    "parameters": {{"param1": "value1"}} or {{}},
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Examples:
User: "What's in my cart cart454?" → {{"tool_name": "getorder", "parameters": {{"cart_id": "cart454"}}, "confidence": 0.9, "reasoning": "User asking about specific cart"}}
User: "What happened to my order 2?" → {{"tool_name": "getorder", "parameters": {{"cart_id": "2"}}, "confidence": 0.85, "reasoning": "User asking about order/cart 2"}}
User: "Hello there" → {{"tool_name": null, "parameters": {{}}, "confidence": 0.0, "reasoning": "General greeting, no tool needed"}}
User: "Multiply 5 and 3" → {{"tool_name": "multiply", "parameters": {{"a": 5, "b": 3}}, "confidence": 0.95, "reasoning": "Clear math operation"}}

JSON Response:"""
    
    return prompt

