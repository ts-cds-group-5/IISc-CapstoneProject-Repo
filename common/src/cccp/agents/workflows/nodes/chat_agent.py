# src/cccp/agents/workflows/chat_agent.py
from langgraph.graph import StateGraph
from cccp.agents.state import AgentState
from cccp.agents.workflows.nodes.chat_node import chat_node
from cccp.agents.workflows.nodes.response_node import response_node
from cccp.agents.workflows.nodes.tool_node import tool_node

def create_chat_agent():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("tool", tool_node)
    workflow.add_node("chat", chat_node)
    workflow.add_node("response", response_node)
    
    # Define flow
    workflow.set_entry_point("tool")
    
    # add conditional edges for tool node to call chat node if state is none
    workflow.add_conditional_edges(
        "tool",
        lambda state: "chat" if state.get("response") is None else "response",
        ["chat", "response"]
    )
    workflow.add_edge("chat", "response")
    
    return workflow.compile()