"""Chat node with proper tool calling agent."""

from cccp.services.model_service import ModelService
from cccp.agents.state import AgentState
from cccp.core.logging import get_logger
from cccp.tools import get_all_tools
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

logger = get_logger(__name__)

class ChatNode:
    """Chat node for processing user input with tool calling agent."""
    
    def __init__(self):
        self.model_service = ModelService()
        self.tools = get_all_tools()
        self._agent_executor = None
    
    def _get_agent_executor(self):
        """Get or create the agent executor."""
        if self._agent_executor is None:
            # Get model
            model = self.model_service.get_model()
            
            # Create a prompt for the agent
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant. You can help with various tasks and have access to tools when needed.\n\nWhen users ask questions:\n1. Provide helpful and accurate responses\n2. Use tools when appropriate for calculations or specific tasks\n3. Be conversational and friendly\n4. If you're unsure about something, say so rather than guessing"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
            
            # Construct the tool-calling agent
            agent = create_tool_calling_agent(model, self.tools, prompt)
            
            # Create an agent executor
            self._agent_executor = AgentExecutor(
                agent=agent, 
                tools=self.tools, 
                verbose=True,
                handle_parsing_errors=True
            )
            
            logger.info(f"Created tool calling agent with {len(self.tools)} tools")
        
        return self._agent_executor
    
    def process(self, state: AgentState) -> AgentState:
        """Process user input and generate response."""
        try:
            logger.info(f"Processing user input: {state['user_input']}")
            
            # Get agent executor
            agent_executor = self._get_agent_executor()
            
            # Invoke the agent executor
            result = agent_executor.invoke({"input": state['user_input']})
            
            # Extract response
            response_text = result.get("output", "No response generated")
            
            # Update state with response
            state["response"] = response_text
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
    

