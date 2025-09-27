# read https://docs.langchain.com/langgraph-platform
# for reference read: https://docs.langchain.com/oss/python/langgraph/application-structure#python-requirements-txt

from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """State for the agent."""
    messages: List[BaseMessage]
    user_input: str
    response: str
    tools: List[str]
    tools_used: List[str]
    tool_results: List[str]
    error: Optional[str]
