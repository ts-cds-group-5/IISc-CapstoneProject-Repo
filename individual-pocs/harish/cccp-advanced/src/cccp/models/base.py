"""Base model classes for CCCP Advanced."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from cccp.core.logging import LoggerMixin
from cccp.core.exceptions import ModelError


class BaseModel(ABC, LoggerMixin):
    """Base class for all models."""
    
    def __init__(self, model_name: str, device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._model = None
        self._tokenizer = None
        self._pipeline = None
        
    @abstractmethod
    def load(self) -> None:
        """Load the model and tokenizer."""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        pass
    
    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._model is not None and self._tokenizer is not None
    
    def unload(self) -> None:
        """Unload the model to free memory."""
        self._model = None
        self._tokenizer = None
        self._pipeline = None
        self.logger.info("Model unloaded")


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

