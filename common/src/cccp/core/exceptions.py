"""Custom exceptions for CCCP Advanced."""


class CCCPException(Exception):
    """Base exception for CCCP Advanced."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ModelError(CCCPException):
    """Exception raised for model-related errors."""
    
    def __init__(self, message: str, model_name: str = None):
        self.model_name = model_name
        super().__init__(message, "MODEL_ERROR")


class ToolError(CCCPException):
    """Exception raised for tool-related errors."""
    
    def __init__(self, message: str, tool_name: str = None):
        self.tool_name = tool_name
        super().__init__(message, "TOOL_ERROR")


class AgentError(CCCPException):
    """Exception raised for agent-related errors."""
    
    def __init__(self, message: str, agent_name: str = None):
        self.agent_name = agent_name
        super().__init__(message, "AGENT_ERROR")


class MCPError(CCCPException):
    """Exception raised for MCP server errors."""
    
    def __init__(self, message: str, mcp_method: str = None):
        self.mcp_method = mcp_method
        super().__init__(message, "MCP_ERROR")


class ConfigurationError(CCCPException):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        super().__init__(message, "CONFIG_ERROR")


class ValidationError(CCCPException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field_name: str = None):
        self.field_name = field_name
        super().__init__(message, "VALIDATION_ERROR")

