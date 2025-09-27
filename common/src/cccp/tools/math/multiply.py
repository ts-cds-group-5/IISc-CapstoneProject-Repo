#implement multiply tool for CCCP Advanced

from cccp.tools.base import MathTool

class MultiplyTool(MathTool):
    """Multiply tool for CCCP Advanced."""
    
    def _get_description(self) -> str:
        return "Multiply two integers"
    
    def _execute_logic(self, a: int, b: int) -> int:
        result = a * b
        self.logger.info(f"Result of multiplying {a} and {b} is {result}")
        return result