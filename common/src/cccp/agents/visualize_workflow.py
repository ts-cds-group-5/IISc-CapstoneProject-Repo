#!/usr/bin/env python3
"""
LangGraph Workflow Visualization Script
Generates visual representations of the chat agent workflow
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cccp.agents.workflows.nodes.chat_agent import create_chat_agent
from cccp.agents.state import AgentState

def visualize_workflow():
    """Generate and display the workflow visualization."""
    print("🔍 Generating LangGraph Workflow Visualization...")
    
    try:
        # Create the agent
        agent = create_chat_agent()
        
        # Method 1: Print the workflow structure
        print("\n📊 Workflow Structure:")
        print("=" * 50)
        graph = agent.get_graph()
        print(f"Nodes: {list(graph.nodes.keys())}")
        print(f"Edges: {list(graph.edges)}")
        print(f"Graph Type: {type(graph).__name__}")
        
        # Method 2: Generate Mermaid diagram
        print("\n🎨 Mermaid Diagram:")
        print("=" * 50)
        mermaid_diagram = generate_mermaid_diagram()
        print(mermaid_diagram)
        
        # Method 3: Save visualization to file
        save_visualization_files(agent)
        
        print("\n✅ Visualization complete!")
        print("📁 Check the generated files:")
        print("   - workflow_mermaid.md")
        print("   - workflow_structure.txt")
        
    except Exception as e:
        print(f"❌ Error generating visualization: {e}")
        return False
    
    return True

def generate_mermaid_diagram():
    """Generate a Mermaid diagram of the workflow."""
    return """
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
- **State**: `AgentState` (user_input, response, tools_used, tool_results, error, status)
"""

def save_visualization_files(agent):
    """Save visualization to files."""
    
    # Save Mermaid diagram
    with open("workflow_mermaid.md", "w") as f:
        f.write("# LangGraph Chat Agent Workflow\n\n")
        f.write(generate_mermaid_diagram())
        f.write("\n## Current Implementation\n\n")
        f.write("The workflow currently has a simple linear flow:\n")
        f.write("- **Chat Node**: Processes user input using the configured model\n")
        f.write("- **Response Node**: Formats and returns the response\n\n")
        f.write("## Future Enhancements\n\n")
        f.write("This structure can be extended to include:\n")
        f.write("- Tool selection and execution\n")
        f.write("- Conditional routing based on input type\n")
        f.write("- Memory management\n")
        f.write("- Error handling and recovery\n")
        f.write("- Multi-step reasoning\n")
    
    # Save structure details
    with open("workflow_structure.txt", "w") as f:
        f.write("LangGraph Workflow Structure\n")
        f.write("=" * 40 + "\n\n")
        graph = agent.get_graph()
        f.write(f"Nodes: {list(graph.nodes.keys())}\n")
        f.write(f"Edges: {list(graph.edges)}\n")
        f.write(f"Graph Type: {type(graph).__name__}\n\n")
        f.write("State Schema:\n")
        f.write("- user_input: str\n")
        f.write("- response: str\n")
        f.write("- tools: List[str]\n")
        f.write("- tools_used: List[str]\n")
        f.write("- tool_results: List[str]\n")
        f.write("- error: Optional[str]\n")
        f.write("- status: Optional[str]\n")

def generate_detailed_workflow():
    """Generate a more detailed workflow including tool usage."""
    return """
```mermaid
graph TD
    A[User Input] --> B{Math Operation?}
    B -->|Yes| C[Execute Math Tool]
    B -->|No| D[Chat Node]
    
    C --> C1[Multiply Tool]
    C --> C2[Add Tool]
    C --> C3[Subtract Tool]
    
    C1 --> E[Math Response]
    C2 --> E
    C3 --> E
    
    D --> D1[Model Service]
    D1 --> D2[Generate Response]
    D2 --> F[Response Node]
    
    E --> G[Final Response]
    F --> G
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
    style C fill:#ffecb3
    style D fill:#fff3e0
    style F fill:#f3e5f5
```

## Complete Chat Flow

1. **User Input**: User sends message
2. **Math Detection**: Check if input contains math operations
3. **Tool Execution**: If math detected, execute appropriate tool
4. **Chat Processing**: If not math, use LangGraph agent
5. **Response Formatting**: Format and return response
"""

if __name__ == "__main__":
    print("🚀 LangGraph Workflow Visualizer")
    print("=" * 40)
    
    success = visualize_workflow()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. View the generated Mermaid diagram in workflow_mermaid.md")
        print("2. Use the diagram in your documentation")
        print("3. Extend the workflow with more nodes as needed")
    else:
        print("\n❌ Visualization failed. Check the error above.")
