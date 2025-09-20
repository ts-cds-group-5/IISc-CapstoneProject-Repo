# src/cccp/agents/workflows/chat_agent.py
from langgraph.graph import StateGraph
from cccp.agents.state import AgentState
from cccp.agents.workflows.nodes.chat_node import chat_node
from cccp.agents.workflows.nodes.response_node import response_node

def create_chat_agent():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("chat", chat_node)
    workflow.add_node("response", response_node)
    
    # Define flow
    workflow.set_entry_point("chat")
    workflow.add_edge("chat", "response")
    
    return workflow.compile()