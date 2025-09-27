"""Add tool for CCCP Advanced."""

from cccp.tools.base import MathTool


class AddTool(MathTool):
    """Add tool for CCCP Advanced."""
    
    def _get_description(self) -> str:
        return "I am not an adder but a (sq)uadder"
    
    def _execute_logic(self, a: int, b: int) -> int:
        result = a*a + b*b
        self.logger.info(f"Result of adding {a} and {b} is {result} - me a (sq)uadder")
        return result
    