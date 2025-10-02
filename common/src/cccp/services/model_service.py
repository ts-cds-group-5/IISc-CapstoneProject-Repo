"""Model service for CCCP Advanced."""

from typing import Dict, Any, Optional, Union
from cccp.core.logging import LoggerMixin
from cccp.core.exceptions import ModelError
from cccp.models.phi2_model import Phi2Model, get_model_instance, reset_model_instance
from cccp.models.ollama_model import OllamaModel, get_ollama_model_instance, is_ollama_running
from cccp.core.config import get_settings


class ModelService(LoggerMixin):
    """Service for managing models."""
    
    def __init__(self, model_type: str = "phi2"):  # Force Phi-2 for testing
        self.model: Optional[Union[Phi2Model, OllamaModel]] = None
        self.model_type = model_type
        self.settings = get_settings()
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the model."""
        try:
            self.logger.info("Initializing model service")
            
            # Determine which model to use
            # if self.model_type == "auto":
            #     # Try Ollama first, fallback to Phi2
            #     if is_ollama_running():
            #         self.logger.info("Ollama detected, using Ollama model")
            #         self.model = get_ollama_model_instance()
            #     else:
            #         self.logger.info("Ollama not available, using Phi2 model")
            #         self.model = get_model_instance()
            # elif self.model_type == "ollama":
            if self.model_type == "auto":
                # Try Ollama first, fallback to Phi2
                if is_ollama_running():
                    self.logger.info("Ollama detected, using Ollama model")
                    self.model = get_ollama_model_instance()
                else:
                    self.logger.info("Ollama not available, using Phi2 model")
                    self.model = get_model_instance()
            elif self.model_type == "phi2":
                self.model = get_model_instance()
            elif self.model_type == "ollama":
                if not is_ollama_running():
                    raise ModelError("Ollama is not running. Please start Ollama first.")
                self.model = get_ollama_model_instance()
            else:
                raise ModelError(f"Unknown model type: {self.model_type}")
            
            self.logger.info("Model service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize model service: {str(e)}")
            raise ModelError(f"Failed to initialize model service: {str(e)}")
    
    def get_model(self) -> Union[Phi2Model, OllamaModel]:
        """Get the current model instance."""
        if not self.model:
            raise ModelError("Model not initialized")
        return self.model
    
    def reload_model(self) -> None:
        """Reload the model."""
        try:
            self.logger.info("Reloading model")
            if self.model:
                self.model.unload()
            
            # Reset singleton instances
            if self.model_type == "phi2":
                reset_model_instance()
            
            # Reinitialize with the same model type
            self._initialize_model()
            self.logger.info("Model reloaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to reload model: {str(e)}")
            raise ModelError(f"Failed to reload model: {str(e)}")
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get the current model status."""
        if not self.model:
            return {
                "status": "not_loaded",
                "model_name": None,
                "device": None,
                "is_loaded": False,
                "model_type": self.model_type
            }
        
        return {
            "status": "loaded" if self.model.is_loaded else "loading",
            "model_name": self.model.model_name,
            "device": self.model.device,
            "is_loaded": self.model.is_loaded,
            "model_type": type(self.model).__name__
        }
    
    def update_model_config(self, **kwargs) -> None:
        """Update model configuration."""
        if not self.model:
            raise ModelError("Model not initialized")
        
        try:
            self.logger.info(f"Updating model config: {kwargs}")
            # Update model configuration
            for key, value in kwargs.items():
                if hasattr(self.model.config, key):
                    setattr(self.model.config, key, value)
                    self.logger.debug(f"Updated {key} to {value}")
            
            self.logger.info("Model config updated successfully")
        except Exception as e:
            self.logger.error(f"Failed to update model config: {str(e)}")
            raise ModelError(f"Failed to update model config: {str(e)}")
    
    def is_ready(self) -> bool:
        """Check if the model service is ready."""
        return self.model is not None and self.model.is_loaded

