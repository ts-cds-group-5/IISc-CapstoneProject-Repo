#chat node that will instantiate model service, get active mode, 
# send input and get response
from cccp.services.model_service import ModelService
from cccp.agents.state import AgentState

def chat_node(state: AgentState) -> AgentState:
    model_service = ModelService()
    model = model_service.get_model()
    
    # Generate response using your existing model
    response = model.generate(state["user_input"])
    
    state["response"] = response
    return state