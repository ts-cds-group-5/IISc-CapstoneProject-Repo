"""Tool execution node for CCCP Advanced."""

from cccp.agents.state import AgentState
from cccp.core.logging import get_logger
from cccp.tools import get_tool
import re

logger = get_logger(__name__)

def tool_node(state: AgentState) -> AgentState:
    """Execute tools based on user input."""
    
    try:
        user_input = state['user_input'].lower()
        
        # Detect math operations
        math_patterns = {
            'addtool': r'add\s+(\d+)\s*(?:and|by|with)?\s*(\d+)',
            'multiplytool': r'multiply\s+(\d+)\s*(?:and|by|with)?\s*(\d+)',
            'subtract': r'subtract\s+(\d+)\s*(?:and|by|with)?\s*(\d+)'
        }
        
        for operation, pattern in math_patterns.items():
            match = re.search(pattern, user_input)
            if match:
                a, b = int(match.group(1)), int(match.group(2))
                logger.info(f"Detected {operation} operation: {a}, {b}")
                
                # Get and execute tool
                tool = get_tool(operation)
                result = tool.run(a=a, b=b)
                
                # Clean up operation name for display
                display_operation = operation.replace('tool', '')
                state["response"] = f"The result of {display_operation}ing {a} and {b} is {result}"
                state["tools_used"] = [operation]
                state["tool_results"] = [str(result)]
                
                return state
        
        # No tool match found, continue to chat
        state["response"] = None  # Signal to continue to chat node
        return state
        
    except Exception as e:
        logger.error(f"Error in tool node: {str(e)}")
        state["error"] = str(e)
        return state