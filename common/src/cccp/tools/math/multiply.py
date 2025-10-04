#implement multiply tool for CCCP Advanced

from cccp.tools.base import BaseCCCPTool
from cccp.core.exceptions import ToolError
from typing import Dict, Any, List
import json
from pydantic import BaseModel, Field

class MultiplyToolInput(BaseModel):
    a: int = Field(..., description="First integer to multiply")
    b: int = Field(..., description="Second integer to multiply")

class MultiplyTool(BaseCCCPTool):
    """Multiply tool for CCCP Advanced."""
    
    # Override Pydantic fields with specific values
    inputs: List[str] = Field(default=["a", "b"], description="Input parameters: a (int), b (int)")
    outputs: List[str] = Field(default=["result"], description="Output: result (int)")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
    
    def _get_description(self) -> str:
        return "Multiply two integers"
    
    def _execute_logic(self, a: int, b: int) -> int:
        result = a * b
        self.logger.info(f"Result of multiplying {a} and {b} is {result}")
        return result
    
    #implement run method
    def run(self, a: int, b: int) -> int:
        self.logger.info(f"run multiply tool with a={a}, b={b}")
        return self._execute_logic(a, b)
    
    #implement arun method
    def arun(self, a: int, b: int) -> int:
        self.logger.info(f"arun multiply tool with a={a}, b={b}")
        return self._execute_logic(a, b)
    
    #implement to_json_string method    
    def to_json_string(self) -> str:
        """Convert the tool to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> 'MultiplyTool':
        """Create a tool from a JSON string."""
        return cls.from_dict(json.loads(data))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary."""
        return {
            "name": self.name,
            "tool_name": self.tool_name,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs
        }
          
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultiplyTool':
        """Create a tool from a dictionary."""
        return cls(**data)
    
