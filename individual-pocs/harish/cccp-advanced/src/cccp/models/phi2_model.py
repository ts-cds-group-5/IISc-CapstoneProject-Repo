"""Phi-2 model implementation for CCCP Advanced."""

import torch
from typing import Optional, Tuple, Any, Dict
from transformers import AutoTokenizer, pipeline, AutoModelForCausalLM

from cccp.core.logging import get_logger
from cccp.core.exceptions import ModelError
from cccp.core.config import get_settings
from cccp.models.base import BaseModel, ModelConfig

logger = get_logger(__name__)


class Phi2Model(BaseModel):
    """Phi-2 model implementation."""
    
    def __init__(
        self, 
        model_name: str = "microsoft/phi-2",
        device: str = "cpu",
        config: Optional[ModelConfig] = None
    ):
        super().__init__(model_name, device)
        self.config = config or ModelConfig()
        self._pipeline = None
    
    def load(self) -> None:
        """Load the Phi-2 model and tokenizer."""
        try:
            self.logger.info(f"Loading Phi-2 model: {self.model_name}")
            
            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.logger.info("Tokenizer loaded successfully")
            
            # Load model
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                dtype=torch.float32,
                device_map=self.device,
                local_files_only=True
            )
            self.logger.info("Model loaded successfully")
            
            # Create pipeline
            self._pipeline = pipeline(
                "text-generation",
                model=self._model,
                tokenizer=self._tokenizer,
                pad_token_id=self._tokenizer.eos_token_id,
                device_map=self.device,
                **self.config.to_dict()
            )
            self.logger.info("Text generation pipeline created successfully")
            
        except Exception as e:
            error_msg = f"Failed to load Phi-2 model: {str(e)}"
            self.logger.error(error_msg)
            raise ModelError(error_msg, self.model_name)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        if not self.is_loaded:
            raise ModelError("Model not loaded. Call load() first.")
        
        try:
            self.logger.info(f"Generating text for prompt: {prompt}")
            
            # Merge config with kwargs
            generation_kwargs = {**self.config.to_dict(), **kwargs}
            
            # Generate text
            outputs = self._pipeline(prompt, num_return_sequences=1, **generation_kwargs)
            
            if not outputs or len(outputs) == 0:
                raise ModelError("No output generated from model")
            
            generated_text = outputs[0]['generated_text']
            self.logger.debug(f"Generated text length: {len(generated_text)}")
            
            return generated_text
            
        except Exception as e:
            error_msg = f"Failed to generate text: {str(e)}"
            self.logger.error(error_msg)
            raise ModelError(error_msg, self.model_name)
    
    def generate_with_prompt_template(self, instruction: str) -> str:
        """Generate text using the task template format."""
        task_template = self._create_task_template(instruction)
        return self.generate(task_template)
    
    def _create_task_template(self, instruction: str) -> str:
        """Create a structured task template."""
        return f"""You are a friendly chatbot assistant that gives structured output.
Your role is to arrange the given task in this structure.
### instruction:
{instruction}

Output:###Response:
"""


# Convenience functions for backward compatibility
def load_phi2_model(model_name: str = "microsoft/phi-2") -> Tuple[Any, Any]:
    """
    Load Phi-2 model and tokenizer (backward compatibility).
    
    Args:
        model_name: Name of the model to load
        
    Returns:
        Tuple of (model, tokenizer)
    """
    logger.warning("load_phi2_model is deprecated. Use Phi2Model class instead.")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            dtype=torch.float32,
            device_map='cpu',
            local_files_only=True
        )
        return model, tokenizer
    except Exception as e:
        raise ModelError(f"Failed to load model: {str(e)}", model_name)


def get_text_generator(model: Any, tokenizer: Any) -> Any:
    """
    Create text generation pipeline (backward compatibility).
    
    Args:
        model: Loaded model
        tokenizer: Loaded tokenizer
        
    Returns:
        Text generation pipeline
    """
    logger.warning("get_text_generator is deprecated. Use Phi2Model class instead.")
    
    try:
        return pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            pad_token_id=tokenizer.eos_token_id,
            device_map="cpu",
            max_length=256,
            truncation=True,
            temperature=0.2,
            repetition_penalty=1.2,
            do_sample=True
        )
    except Exception as e:
        raise ModelError(f"Failed to create pipeline: {str(e)}")


# Global model instance (singleton pattern)
_model_instance: Optional[Phi2Model] = None


def get_model_instance() -> Phi2Model:
    """Get the global model instance (singleton)."""
    global _model_instance
    
    if _model_instance is None:
        settings = get_settings()
        _model_instance = Phi2Model(
            model_name=settings.model_name,
            device=settings.model_device,
            config=ModelConfig(
                max_length=settings.model_max_length,
                temperature=settings.model_temperature,
                repetition_penalty=settings.model_repetition_penalty
            )
        )
        _model_instance.load()
    
    return _model_instance

