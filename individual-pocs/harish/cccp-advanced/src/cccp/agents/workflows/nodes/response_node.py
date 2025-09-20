"""Response formatting node for the chat agent."""

from cccp.agents.state import AgentState
from cccp.core.logging import get_logger

logger = get_logger(__name__)

def response_node(state: AgentState) -> AgentState:
    """Format and finalize the response."""
    logger.info("Formatting response")
    
    # For now, just pass through the response
    # In the future, we can add response formatting, validation, etc.
    
    logger.debug(f"Final response: {state.get('response', 'No response generated')}")
    return state
