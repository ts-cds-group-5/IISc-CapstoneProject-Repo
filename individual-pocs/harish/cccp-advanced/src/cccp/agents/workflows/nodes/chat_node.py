#chat node that will instantiate model service, get active mode, 
# send input and get response
from cccp.services.model_service import ModelService
from cccp.agents.state import AgentState
from cccp.core.logging import get_logger

logger = get_logger(__name__)

def chat_node(state: AgentState) -> AgentState:
    """Process user input and generate response."""
    
    try:
        logger.info(f"Processing user input: {state['user_input']}")
        model_service = ModelService()
        model = model_service.get_model()

        # Bind tools to the model for automatic tool calling
        from cccp.tools import get_all_tools
        tools = get_all_tools()
        model_with_tools = model.bind_tools(tools)
        logger.info(f"Tools bound to model: {[getattr(tool, 'name', getattr(tool, 'tool_name', str(tool))) for tool in tools]}")

        # Generate response using model with tools
        response = model_with_tools.generate(state["user_input"])

        # Update state with response
        state["response"] = response
        logger.info("Response generated successfully")

        return state

    except Exception as e:
        logger.error(f"Error in chat node: {str(e)}")
        state["error"] = str(e)
        state["status"] = "error"
        state["response"] = "Error in chat node when processing request:  " + str(e)
        return state
    

