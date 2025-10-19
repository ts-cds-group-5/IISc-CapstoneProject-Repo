# Custom Tool Calling Implementation Plan

## 🎯 **CURRENT STATE (WIP Commit: 831412c)**
- ✅ Math tools working via manual pattern matching (`tool_node`)
- ❌ General chat failing with JSON serialization errors
- ✅ Pydantic models implemented for LangChain compatibility
- ✅ Prompt template system created
- ✅ Models updated for better LangChain integration

## 🔍 **KEY FINDINGS**
- **Llama3.2** and **Phi-2** are **text-based models**, NOT structured output models
- They cannot natively support LangChain's `create_tool_calling_agent`
- **Custom implementation** required for tool calling

## 🏗️ **IMPLEMENTATION STRATEGY: Option A - Custom Tool Calling**

### **Phase 1: Basic Tool Calling (Immediate)**
```python
# Target: Structured JSON output for tool calls
{
    "intent": "tool_usage",
    "tool_name": "get_order",
    "parameters": {
        "order_id": "22345",
        "user_id": "user123"
    },
    "confidence": 0.95
}
```

### **Phase 2: Intent Classification (Next)**
```python
# Target: Intent classification output
{
    "intent": "order_inquiry",
    "entities": {
        "order_id": "22345",
        "time_reference": "day before"
    },
    "confidence": 0.88,
    "suggested_tools": ["get_order", "get_user_orders"]
}
```

### **Phase 3: Advanced Features (Future)**
```python
# Target: Multi-step reasoning
{
    "intent": "complex_query",
    "reasoning": "User wants order details, need to authenticate first",
    "steps": [
        {"action": "authenticate_user", "parameters": {"user_id": "user123"}},
        {"action": "get_order", "parameters": {"order_id": "22345"}}
    ]
}
```

## 🛠️ **IMPLEMENTATION STEPS**

### **Step 1: Create Custom Tool Calling Agent**
- File: `src/cccp/agents/custom_tool_calling_agent.py`
- Class: `CustomToolCallingAgent`
- Methods:
  - `parse_response()` - Parse LLM JSON output
  - `execute_tool()` - Execute tool calls
  - `handle_intent()` - Handle intent classification

### **Step 2: Implement get_order Tool**
- File: `src/cccp/tools/order/get_order.py`
- Features:
  - User authentication
  - Order ID validation
  - Order ownership verification
  - Database query (PostgreSQL with pgvector)

### **Step 3: Update Chat Node**
- Replace `create_tool_calling_agent` with `CustomToolCallingAgent`
- Add structured JSON parsing
- Add error handling

### **Step 4: Add Intent Classification**
- File: `src/cccp/agents/intent_classifier.py`
- Analyze conversation chunks
- Classify intents (order_inquiry, general_chat, tool_usage, etc.)

## 📋 **REQUIREMENTS ADDRESSED**

### **1. get_order Tool**
- ✅ Order validation
- ✅ Basic user authentication
- ✅ Database integration ready

### **2. Structured JSON Output**
- ✅ Perfect for intent classification
- ✅ Easy to parse and process
- ✅ Extensible for future features

### **3. Error Handling**
- ✅ Tool execution errors
- ✅ Parsing errors
- ✅ Authentication errors
- ✅ Database errors

## 🚀 **ADVANTAGES OF THIS APPROACH**

1. **Model Agnostic**: Works with any text-based model
2. **Full Control**: Custom logic for tool calling
3. **Intent Classification Ready**: JSON format perfect for this
4. **Gradual Enhancement**: Start simple, add complexity
5. **Future-Proof**: Easy to add RAG, memory, etc.

## 📁 **FILES TO CREATE/MODIFY**

### **New Files:**
- `src/cccp/agents/custom_tool_calling_agent.py`
- `src/cccp/agents/intent_classifier.py`
- `src/cccp/tools/order/get_order.py`
- `src/cccp/tools/order/__init__.py`

### **Modified Files:**
- `src/cccp/agents/workflows/nodes/chat_node.py`
- `src/cccp/agents/workflows/nodes/tool_node.py` (keep as fallback)
- `src/cccp/api/routes/chat.py`

## 🎯 **SUCCESS CRITERIA**

1. **Math tools work** (already working)
2. **General chat works** without JSON errors
3. **get_order tool works** with auth/validation
4. **Intent classification works** for conversation chunks
5. **Error handling works** gracefully

## 📝 **NEXT ACTIONS**

1. Create `CustomToolCallingAgent` class
2. Implement `get_order` tool
3. Update chat node to use custom agent
4. Test with both math and general chat
5. Add intent classification
6. Add comprehensive error handling

---
**Created**: 2025-01-28
**Status**: Ready for implementation
**Commit**: 831412c (WIP: Tool calling architecture refactoring)

