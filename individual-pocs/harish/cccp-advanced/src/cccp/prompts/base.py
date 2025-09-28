"""Base prompt template classes for CCCP Advanced."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from cccp.core.logging import LoggerMixin

class BasePromptTemplate(LoggerMixin, ABC):
    """Base class for all prompt templates."""
    
    def __init__(self, template: str, **kwargs):
        self.template = template
        self.kwargs = kwargs
        self._prompt_template = None
        self._initialize_template()
    
    @abstractmethod
    def _initialize_template(self) -> None:
        """Initialize the prompt template."""
        pass
    
    @abstractmethod
    def format_messages(self, **kwargs) -> List[BaseMessage]:
        """Format messages for the template."""
        pass
    
    def get_template(self) -> PromptTemplate:
        """Get the underlying prompt template."""
        return self._prompt_template

class SystemPromptTemplate(BasePromptTemplate):
    """System prompt template for setting context and behavior."""
    
    def _initialize_template(self) -> None:
        """Initialize system prompt template."""
        self._prompt_template = PromptTemplate(
            input_variables=self._extract_variables(),
            template=self.template
        )
    
    def _extract_variables(self) -> List[str]:
        """Extract variables from template string."""
        import re
        return re.findall(r'\{(\w+)\}', self.template)
    
    def format_messages(self, **kwargs) -> List[BaseMessage]:
        """Format system message."""
        formatted_text = self._prompt_template.format(**kwargs)
        return [SystemMessage(content=formatted_text)]

class UserPromptTemplate(BasePromptTemplate):
    """User prompt template for user inputs."""
    
    def _initialize_template(self) -> None:
        """Initialize user prompt template."""
        self._prompt_template = PromptTemplate(
            input_variables=self._extract_variables(),
            template=self.template
        )
    
    def _extract_variables(self) -> List[str]:
        """Extract variables from template string."""
        import re
        return re.findall(r'\{(\w+)\}', self.template)
    
    def format_messages(self, **kwargs) -> List[BaseMessage]:
        """Format user message."""
        formatted_text = self._prompt_template.format(**kwargs)
        return [HumanMessage(content=formatted_text)]
