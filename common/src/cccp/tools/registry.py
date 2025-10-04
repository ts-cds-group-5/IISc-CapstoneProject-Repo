#implement tool registry for CCCP Advanced
# self-registering tools so that LLM can use them
#LLM uses the tools names and descriptions to call the tools

from typing import Dict, List, Type, Any
from cccp.tools.base import BaseCCCPTool
from cccp.tools.math.add import AddTool
from cccp.tools.math.multiply import MultiplyTool
# from cccp.tools.order.get_order import GetOrderTool  # Temporarily disabled
from cccp.core.logging import get_logger

logger = get_logger(__name__)

class ToolRegistry:
    """Registry for tools."""
    def __init__(self):
        self._tools: Dict[str, Type[BaseCCCPTool]] = {} #tools dictionary with name as key and tool class as value
        self._instances: Dict[str, BaseCCCPTool] = {} #instances dictionary with name as key and tool instance as value
        self.register_default_tools()
        
    def register_default_tools(self):

        # """Register default tools."""
        # default_tools = [
        #     MultiplyTool,
        #     AddTool,
        #     SubtractTool,
        # ]
        
        # for tool_class in default_tools:
        #     self.register_tool(tool_class)

        #find all tools that are subclasses of BaseCCCPTool and add them to default tools[]
        default_tools = []
        #check if the tool is a subclass of BaseCCCPTool 
        # todo: check if this is correct way? Adding all tools that are subclasses of BaseCCCPTool to default tools[]
        for tool in BaseCCCPTool.__subclasses__():
            if issubclass(tool, BaseCCCPTool):
                self.register_tool(tool)

        logger.info(f"ToolRegistry-> registered default tools: {list(self._tools.keys())}")

    def register_tool(self, tool_class: Type[BaseCCCPTool]):
        """Register a new tool class."""
        # Create a temporary instance to get the proper tool name
        # tool name is tool_name instead of name (addtool instead of add)
            # temp_instance = tool_class()
            # tool_name = temp_instance.name
            # self._tools[tool_name] = tool_class
            # logger.info(f"Registered tool: {tool_name}")
        temp_instance = tool_class()
        tool_name = temp_instance.tool_name  # Use tool_name instead of name
        self._tools[tool_name] = tool_class
        logger.info(f"Registered tool: {tool_name}")
        
    def get_tool(self, tool_name: str) -> BaseCCCPTool:
        """Get a tool instance by name."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not registered")
        
        if tool_name not in self._instances:
            try:
                # Create tool instance with proper initialization
                tool_class = self._tools[tool_name]
                self._instances[tool_name] = tool_class()
                logger.info(f"Created tool instance: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to create tool instance {tool_name}: {e}")
                raise ValueError(f"Failed to create tool instance {tool_name}: {e}")
        
        return self._instances[tool_name]
        
    def get_all_tools(self) -> List[BaseCCCPTool]:
        """Get all available tool instances."""
        return [self.get_tool(name) for name in self._tools.keys()]
        
    def get_tool_names(self) -> List[str]:
        """Get all available tool names."""
        return list(self._tools.keys())
        
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get tool information."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not registered")
            
        tool = self.get_tool(tool_name)
        return {
            "name": tool_name,
            "description": tool.description,
            "available": True,
            "class": tool.__class__.__name__
        }


# Global registry instances. This makes it easy to access the registry from anywhere.
# make this singleton? --> @todo: Think and implement singleton pattern. Read about singleton in python

tool_registry = ToolRegistry()

# Convenience functions
def get_tool(tool_name: str) -> BaseCCCPTool:
    """Get a tool by name."""
    return tool_registry.get_tool(tool_name)

def get_all_tools() -> List[BaseCCCPTool]:
    """Get all available tools."""
    return tool_registry.get_all_tools()

def register_tool(tool_class: Type[BaseCCCPTool]):
    """Register a new tool."""
    tool_registry.register_tool(tool_class)

