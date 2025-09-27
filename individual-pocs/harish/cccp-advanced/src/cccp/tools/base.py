from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from langchain_core.tools import BaseTool
from cccp.core.logging import LoggerMixin
from cccp.core.exceptions import ToolError

class BaseCCCPTool(LoggerMixin, BaseTool):
    """Base class for all CCCP tools."""

    def __init__(self, **kwargs):
        # Set name and description before calling super().__init__
        self.tool_name = self.__class__.__name__.lower().replace('tool', '')
        self.description = self._get_description()
        
        # Initialize with LangChain-compatible attributes
        super().__init__(
            name=self.tool_name,
            description=self.description,
            **kwargs
        )
    
    @abstractmethod
    def _get_description(self) -> str:
        """Get the description of the tool."""
        pass
    
    @abstractmethod
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate tool inputs."""
        pass

    #implement run method
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Run the tool."""
        pass

    #implement arun method
    @abstractmethod
    def arun(self, *args ,**kwargs) -> Any:
        """Run the tool asynchronously."""
        pass

    #implement to_dict method
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary."""
        pass

    #implement from_dict method
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseCCCPTool':
        """Create a tool from a dictionary."""
        pass

    #implement to_json method
    @abstractmethod
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        pass

    #implement from_json method
    @classmethod
    @abstractmethod
    def from_json(cls, data: str) -> 'BaseCCCPTool':
        """Create a tool from a JSON string."""
        pass

    #implement _execute_logic method
    @abstractmethod
    def _execute_logic(self, **kwargs) -> Any:
        """Execute the tool."""
        pass    

#implement MathTool class - this is a base class for mathematical tools
class MathTool(BaseCCCPTool):
    """Base class for mathematical tools."""
    
    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate mathematical inputs."""
        a = kwargs.get("a")
        b = kwargs.get("b")

        if a is None or b is None:
            raise ToolError("Both 'a' and 'b' parameters are required.", self.tool_name)
        
        try:
            a_int = int(a)
            b_int = int(b)
            return {"a": a_int, "b": b_int}
        except (ValueError, TypeError) as e:
            raise ToolError(f"Invalid input: {e}", self.tool_name)
    
    def run(self, a: int, b: int, **kwargs) -> Any:
        """Run the mathematical tool."""
        try:
            # Validate inputs
            validated_inputs = self._validate_inputs(a=a, b=b, **kwargs)
            
            # Execute the specific mathematical operation
            result = self._execute_logic(**validated_inputs)
            
            self.logger.info(f"Tool {self.tool_name} executed successfully with result: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing tool {self.tool_name}: {str(e)}")
            raise ToolError(f"Tool execution failed: {str(e)}", self.tool_name)
    
    async def arun(self, a: int, b: int, **kwargs) -> Any:
        """Async version of run method."""
        return self.run(a, b, **kwargs)

#implement Order tool class - this is a base class to validate existing order inputs
#use it for get_order, update_order, cancel_order, schedule_order_delivery, etc.
#THIS TOOL SHOULD NOT BE USED FOR CREATING NEW ORDERS
# class OrderTool(BaseCCCPTool, ABC):
#     """Base class for mathematical tools."""
#     def _validate_inputs(self, order_id: Any, **kwargs) -> Dict[str, Any]:
#         """Validate mathematical inputs."""
#         try:
#             order_id = int(order_id)
#             #add code to check if order exists in the database - #@todo

#             return {"a": a_int, "b": b_int}
#         except (ValueError, TypeError) as e:
#             raise ToolError(f"Invalid input: {e}", self.tool_name)  

# class CreateOrderTool(BaseCCCPTool, ABC):
#     """Base class for creating new orders."""
#     def _validate_inputs(self, order_req_id: Any, **kwargs) -> Dict[str, Any]:
#         """Validate creating new orders."""
#         try:
#             order_req_id = int(order_req_id)


#             return {"order_req_id": order_req_id}
#         except (ValueError, TypeError) as e:
#             raise ToolError(f"Invalid input: {e}", self.tool_name)  

