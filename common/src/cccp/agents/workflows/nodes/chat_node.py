"""Chat node with custom tool calling agent."""

from cccp.agents.state import AgentState
from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
from cccp.core.logging import get_logger

logger = get_logger(__name__)

class ChatNode:
    """Chat node for processing user input with custom tool calling agent."""
    
    def __init__(self):
        self.custom_agent = CustomToolCallingAgent()
        logger.info("ChatNode initialized with CustomToolCallingAgent")
    
    def process(self, state: AgentState) -> AgentState:
        """Process user input and generate response."""
        try:
            logger.info(f"Processing user input: {state['user_input']}")
            
            # Process with custom tool calling agent
            result = self.custom_agent.process_user_input(state['user_input'])
            
            # Extract response based on intent
            if result.get("intent") == "tool_usage":
                response_text = result.get("response", "Tool executed successfully")
                # Track tool usage
                state["tools_used"] = state.get("tools_used", []) + [result.get("tool_name", "unknown")]
                state["tool_results"] = state.get("tool_results", []) + [str(result.get("result", ""))]
            elif result.get("intent") == "general_chat":
                response_text = result.get("response", "I'm not sure how to help with that.")
            else:
                response_text = result.get("response", "Error processing request")
            
            # Update state with response
            state["response"] = response_text
            state["status"] = "success"
            logger.info("Response generated successfully")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in chat node: {str(e)}")
            state["error"] = str(e)
            state["status"] = "error"
            state["response"] = f"Error in chat node when processing request: {str(e)}"
            return state

# Create global instance
chat_node_instance = ChatNode()

def chat_node(state: AgentState) -> AgentState:
    """Chat node function for LangGraph compatibility."""
    return chat_node_instance.process(state)
    

