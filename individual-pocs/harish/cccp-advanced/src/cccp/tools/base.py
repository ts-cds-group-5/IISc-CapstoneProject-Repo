from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from langchain_core.tools import BaseTool
from cccp.core.logging import LoggerMixin
from cccp.core.exceptions import ToolError

class BaseCCCPTool(LoggerMixin, BaseTool):
    """Base class for all CCCP tools."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tool_name = self.__class__.__name__.lower().replace('tool', '')
        self.description = self._get_description()
    
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

