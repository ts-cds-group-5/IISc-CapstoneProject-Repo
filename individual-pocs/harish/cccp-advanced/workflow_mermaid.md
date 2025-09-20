# LangGraph Chat Agent Workflow


```mermaid
graph TD
    A[User Input] --> B[Chat Node]
    B --> C[Response Node]
    C --> D[Final Response]
    
    subgraph "Chat Node"
        B1[Model Service]
        B2[Generate Response]
        B1 --> B2
    end
    
    subgraph "Response Node"
        C1[Format Response]
        C2[Add Metadata]
        C1 --> C2
    end
    
    style A fill:#e1f5fe
    style D fill:#c8e6c9
    style B fill:#fff3e0
    style C fill:#f3e5f5
```

## Workflow Description

1. **User Input**: User sends a chat request
2. **Chat Node**: 
   - Gets model instance (Ollama or Phi-2)
   - Generates response using the model
3. **Response Node**: 
   - Formats the final response
   - Adds metadata (execution time, model used, etc.)
4. **Final Response**: Returns structured response to user

## Current Flow
- **Entry Point**: `chat` node
- **Flow**: `chat` → `response`
- **State**: `AgentState` (messages, user_input, response, tools_used, error)

## Current Implementation

The workflow currently has a simple linear flow:
- **Chat Node**: Processes user input using the configured model
- **Response Node**: Formats and returns the response

## Future Enhancements

This structure can be extended to include:
- Tool selection and execution
- Conditional routing based on input type
- Memory management
- Error handling and recovery
- Multi-step reasoning
