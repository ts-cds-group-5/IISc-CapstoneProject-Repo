"""Base model classes for CCCP Advanced."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Union,Optional
from cccp.core.logging import LoggerMixin
from cccp.core.exceptions import ModelError
from pydantic import Field
from cccp.core.config import get_settings

#from langchain_core.language_models.base import BaseLanguageModel
from cccp.tools import get_all_tools, get_tool, tool_registry
#implement BaseChatModel for BaseModel and use it in phi2_model.py and ollama_model.py
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages.base import BaseMessage
from langchain_core.tools import BaseTool

class ModelConfig:
    """Configuration for model parameters."""
    
    def __init__(
        self,
        max_length: int = 256,
        temperature: float = 0.2,
        repetition_penalty: float = 1.2,
        do_sample: bool = True,
        truncation: bool = True,
        **kwargs
    ):
        self.max_length = max_length
        self.temperature = temperature
        self.repetition_penalty = repetition_penalty
        self.do_sample = do_sample
        self.truncation = truncation
        self.extra_kwargs = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "max_length": self.max_length,
            "temperature": self.temperature,
            "repetition_penalty": self.repetition_penalty,
            "do_sample": self.do_sample,
            "truncation": self.truncation,
            **self.extra_kwargs
        }

#inherit BaseLanguageModel for BaseModel and use it in phi2_model.py and ollama_model.py
class BaseModel(LoggerMixin, BaseChatModel):
    """Base class for all models."""
    # Declare Pydantic fields properly
    model_name: str = Field(..., description="The name of the model")
    device: str = Field(default="cpu", description="The device to use for the model")
    config: Optional[ModelConfig] = Field(default=None, description="Model configuration")

    def __init__(self, model_name: str, device: str = "cpu", config: Optional[ModelConfig] = None, **kwargs):
        #add model_name and device to __init__ by passing them to super().__init__ through kwargs: pydantic BaseModel
        self.logger.info(f"BaseModel {get_settings().model_name} , device {get_settings().model_device} and kwargs {kwargs}")

        super().__init__(model_name=model_name, device=device, config=config, **kwargs)
        # self.model_name = model_name
        # self.device = device
        self._model = None
        self._tokenizer = None
        self._pipeline = None
        self._tools = []    # Initialize empty list to store tools to be used by LLM

        #call BaseChatModel __init__to set model name and device and all kw
        #super().__init__(**kwargs)
        self.logger.info(f"Model {self.model_name} initialized with device {self.device} and kwargs {kwargs}")
        
    @abstractmethod
    def load(self) -> None:
        """Load the model and tokenizer."""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        pass
    #implement required methods for BaseChatModel
    @abstractmethod
    def _generate(self, 
    messages: List[BaseMessage], 
    stop: Optional[List[str]]=None,
    run_manager: Optional[Any]=None,
    **kwargs: Any) -> Any:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    def _llm_type(self) -> str:
        """Return the type of LLM."""
        pass


#bind all tools to the LLM using bind_tools of BaseChatModel
    # def bind_tools(self, tools: List[Any]) -> None:
    #     """Bind tools to the LLM is not implemented in the base class."""
    #     if tools is None:
    #         tools = get_all_tools()
        
    #     self.tools = tools
    #     self.logger.info(f"Tools bound to LLM: {[tool.name for tool in tools] }")
  # Tool binding method
    def bind_tools(
        self, 
        tools: Optional[Sequence[Union[BaseTool, Dict[str, Any]]]] = None,
        **kwargs: Any
    ) -> Runnable[LanguageModelInput, Any]:
        """Bind tools to the LLM."""
        if tools is None:
            # Get tools from registry
            tools = get_all_tools()
        
        # Store tools for later use
        self._tools = list(tools)
        self.logger.info(f"Tools bound to LLM: {[getattr(tool, 'name', str(tool)) for tool in self._tools]}")
        return self                # Return self to maintain chainability

    def get_tools(self) -> List[Any]:
        """Get currently bound tools."""
        return self._tools      

    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._model is not None and self._tokenizer is not None
    
    def unload(self) -> None:
        """Unload the model to free memory."""
        self._model = None
        self._tokenizer = None
        self._pipeline = None
        self._tools = []
        self.logger.info("Model unloaded")