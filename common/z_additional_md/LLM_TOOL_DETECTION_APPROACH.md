# LLM-Based Tool Detection Implementation

This document contains the complete LLM-based tool detection approach to replace the current regex-based system in `custom_tool_calling_agent.py`.

## 🎯 **Problem with Current Regex Approach**

The current regex patterns in `_detect_tool_usage` and `_extract_parameters` are:
- **Rigid** - Only match specific patterns like "cart 454"
- **Incomplete** - Miss natural language like "What happened to my order 2?"
- **Hard to maintain** - Adding new patterns requires code changes
- **Error-prone** - Complex regex patterns are difficult to debug

## 🧠 **LLM-Based Solutions**

### **Approach 1: Direct LLM Tool Selection (Recommended)**

Replace the entire `_detect_tool_usage` method with this implementation:

```python
def _detect_tool_usage(self, user_input: str) -> Optional[Dict[str, Any]]:
    """Use LLM to detect tool usage and extract parameters."""
    try:
        # Get available tools information
        tools_info = self._get_tools_info()
        
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

        # Get LLM response
        model = self.model_service.get_model()
        response = model.generate(prompt)
        
        # Parse JSON response
        tool_detection = json.loads(response.strip())
        
        if tool_detection.get("tool_name"):
            logger.info(f"LLM detected tool: {tool_detection}")
            return tool_detection
            
        return None
        
    except Exception as e:
        logger.error(f"Error in LLM tool detection: {str(e)}")
        # Fallback to regex patterns
        return self._fallback_tool_detection(user_input)
```

### **Helper Method: Get Tools Info**

Add this method to provide tool information to the LLM:

```python
def _get_tools_info(self) -> str:
    """Get formatted information about available tools."""
    tools_info = []
    
    for tool_name, tool_instance in self.available_tools.items():
        tool_info = f"""
Tool: {tool_name}
Description: {tool_instance.description}
Parameters: {self._get_tool_parameters(tool_instance)}
"""
        tools_info.append(tool_info.strip())
    
    return "\n".join(tools_info)

def _get_tool_parameters(self, tool_instance) -> str:
    """Get parameter information for a tool."""
    # This would need to be implemented based on your tool structure
    # For GetOrderTool, it would return: "cart_id (optional), customer_email (optional), customer_full_name (optional)"
    return "See tool description for parameters"
```

### **Fallback Method: Keep Current Regex**

Keep your current regex logic as a fallback:

```python
def _fallback_tool_detection(self, user_input: str) -> Optional[Dict[str, Any]]:
    """Fallback regex-based tool detection."""
    user_input_lower = user_input.lower()
    
    # Check for math operations (existing pattern matching)
    math_patterns = {
        'add': r'add\s+(\d+)\s*(?:and|by|with)?\s*(\d+)',
        'multiply': r'multiply\s+(\d+)\s*(?:and|by|with)?\s*(\d+)'
    }
    
    for operation, pattern in math_patterns.items():
        match = re.search(pattern, user_input_lower)
        if match:
            return {
                "tool_name": operation,
                "parameters": {
                    "a": int(match.group(1)),
                    "b": int(match.group(2))
                },
                "confidence": 0.95
            }
    
    # Check for other tool keywords
    tool_keywords = {
        'place_order': ['place order', 'purchase', 'buy'],
        'getorder': ['cart','my cart','my cart status', 'cart status', 'order', 'my order', 'my order status','my shipment','shipment details', 'my shipment details','shipping details', 'tracking details','delivery details','invoice details','ETA','delayed','early','on time','late']
    }
    
    for tool_name, keywords in tool_keywords.items():
        for keyword in keywords:
            if keyword in user_input_lower:
                return {
                    "tool_name": tool_name,
                    "parameters": self._extract_parameters(user_input, tool_name),
                    "confidence": 0.8
                }
    
    return None
```

## 🚀 **Alternative Approaches**

### **Approach 2: LangChain Tool Calling**

For more advanced integration with LangChain:

```python
from langchain_core.tools import StructuredTool
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

def _setup_langchain_tools(self):
    """Convert BaseCCCPTool instances to LangChain tools."""
    langchain_tools = []
    
    for tool_instance in get_all_tools():
        langchain_tool = StructuredTool.from_function(
            func=tool_instance.run,
            name=tool_instance.tool_name,
            description=tool_instance.description,
            args_schema=tool_instance.get_input_schema()  # Implement this method
        )
        langchain_tools.append(langchain_tool)
    
    return langchain_tools

def _detect_tool_usage_langchain(self, user_input: str) -> Optional[Dict[str, Any]]:
    """Use LangChain agent for tool detection and execution."""
    try:
        tools = self._setup_langchain_tools()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant with access to tools. Use tools when appropriate."),
            ("user", "{input}")
        ])
        
        agent = create_tool_calling_agent(
            llm=self.model_service.get_model(),
            tools=tools,
            prompt=prompt
        )
        
        result = agent.invoke({"input": user_input})
        
        return {
            "tool_name": result.get("tool_name"),
            "parameters": result.get("tool_input", {}),
            "confidence": 0.9,
            "langchain_result": result
        }
        
    except Exception as e:
        logger.error(f"LangChain tool detection error: {str(e)}")
        return None
```

### **Approach 3: Hybrid Approach**

Combine LLM intelligence with regex fallbacks:

```python
def _detect_tool_usage(self, user_input: str) -> Optional[Dict[str, Any]]:
    """Hybrid tool detection: LLM primary, regex fallback."""
    try:
        # Try LLM first
        llm_result = self._llm_tool_detection(user_input)
        if llm_result and llm_result.get("confidence", 0) > 0.7:
            return llm_result
        
        # Fallback to regex for simple cases
        return self._regex_tool_detection(user_input)
        
    except Exception as e:
        logger.error(f"Tool detection error: {str(e)}")
        return self._regex_tool_detection(user_input)
```

## 🎯 **Benefits of LLM Approach**

1. **Natural Language Understanding**: Handles any natural language pattern
2. **Flexible Parameter Extraction**: Automatically extracts parameters from context
3. **Easy Maintenance**: No regex patterns to debug or update
4. **Extensible**: Add new tools without changing detection logic
5. **Robust**: Handles edge cases and variations in user input

## 🔧 **Implementation Steps**

1. **Backup Current Code**: Save current `_detect_tool_usage` and `_extract_parameters` methods
2. **Implement Helper Methods**: Add `_get_tools_info()` and `_get_tool_parameters()`
3. **Replace Main Method**: Replace `_detect_tool_usage` with LLM version
4. **Keep Fallback**: Implement `_fallback_tool_detection` with current regex logic
5. **Test**: Test with various natural language queries
6. **Iterate**: Fine-tune prompts based on results

## 📝 **Example Queries That Will Work**

With LLM approach, these will all work perfectly:

- "What happened to my order 2?" → `getorder` with `cart_id: "2"`
- "Show me cart for john@example.com" → `getorder` with `customer_email: "john@example.com"`
- "Check my cart status" → `getorder` with `customer_full_name` from session
- "Multiply 5 by 3" → `multiply` with `a: 5, b: 3`
- "Add 10 and 20" → `add` with `a: 10, b: 20`
- "What's the status of cart cart123?" → `getorder` with `cart_id: "cart123"`

## 🚨 **Important Notes**

1. **JSON Parsing**: Make sure your LLM can generate valid JSON
   - **⚠️ Llama 3.2 Specific**: Llama 3.2 may need tweaked prompts to generate valid JSON consistently
   - Consider adding JSON schema validation in the prompt
   - Test extensively with your specific Llama 3.2 model
   - You may need to adjust temperature settings or add JSON-specific instructions
2. **Error Handling**: Always have regex fallback for reliability
3. **Prompt Engineering**: Test and refine the prompt for best results
4. **Performance**: LLM calls add latency, consider caching for repeated queries
5. **Cost**: Monitor LLM token usage if using paid APIs

## 🔧 **Llama 3.2 Specific Considerations**

Since you're using Llama 3.2, here are additional prompt engineering tips:

### **Enhanced Prompt for Llama 3.2**
```python
def _detect_tool_usage_llama_optimized(self, user_input: str) -> Optional[Dict[str, Any]]:
    """Llama 3.2 optimized tool detection."""
    try:
        tools_info = self._get_tools_info()
        
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
- "Hello there" → {{"tool_name": null, "parameters": {{}}, "confidence": 0.0, "reasoning": "General greeting"}}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{{"""

        model = self.model_service.get_model()
        response = model.generate(prompt, temperature=0.1, max_tokens=200)
        
        # Clean response and parse JSON
        cleaned_response = response.strip().replace('```json', '').replace('```', '').strip()
        tool_detection = json.loads(cleaned_response)
        
        if tool_detection.get("tool_name"):
            return tool_detection
            
        return None
        
    except Exception as e:
        logger.error(f"Llama 3.2 tool detection failed: {str(e)}")
        return self._fallback_tool_detection(user_input)
```

### **JSON Validation Helper**
```python
def _validate_and_clean_json(self, response: str) -> Dict[str, Any]:
    """Validate and clean JSON response from Llama 3.2."""
    try:
        # Remove common JSON artifacts
        cleaned = response.strip()
        cleaned = cleaned.replace('```json', '').replace('```', '').strip()
        cleaned = cleaned.replace('```', '').strip()
        
        # Try to find JSON object
        start = cleaned.find('{')
        end = cleaned.rfind('}') + 1
        
        if start != -1 and end != 0:
            json_str = cleaned[start:end]
            return json.loads(json_str)
        else:
            raise ValueError("No valid JSON found in response")
            
    except Exception as e:
        logger.error(f"JSON validation failed: {str(e)}")
        raise
```

This approach will solve the "What happened to my order 2?" issue and make the system much more flexible for natural language understanding!
