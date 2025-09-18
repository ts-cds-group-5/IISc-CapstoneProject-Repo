"""Ollama model implementation for CCCP Advanced."""

import requests
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

from cccp.core.logging import get_logger
from cccp.core.exceptions import ModelError
from cccp.core.config import get_settings
from cccp.models.base import BaseModel, ModelConfig

logger = get_logger(__name__)


class OllamaModel(BaseModel):
    """Ollama model implementation for local LLM inference."""
    
    def __init__(
        self, 
        model_name: str = "llama3.2:latest",
        device: str = "cpu",  # Ollama handles device management
        config: Optional[ModelConfig] = None,
        ollama_base_url: str = "http://localhost:11434"
    ):
        super().__init__(model_name, device)
        self.config = config or ModelConfig()
        self.ollama_base_url = ollama_base_url
        self._model_loaded = False
        
    def load(self) -> None:
        """Load the Ollama model (check if it's available)."""
        try:
            self.logger.info(f"Checking Ollama model: {self.model_name}")
            
            # Check if Ollama is running
            if not self._check_ollama_running():
                raise ModelError("Ollama server is not running. Please start Ollama first.")
            
            # Check if model exists
            if not self._check_model_exists():
                self.logger.info(f"Model {self.model_name} not found. Pulling from Ollama...")
                self._pull_model()
            
            # Test model with a simple prompt
            self._test_model()
            
            self._model_loaded = True
            self.logger.info(f"Ollama model {self.model_name} loaded successfully")
            
        except Exception as e:
            error_msg = f"Failed to load Ollama model: {str(e)}"
            self.logger.error(error_msg)
            raise ModelError(error_msg, self.model_name)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt using Ollama."""
        if not self.is_loaded:
            raise ModelError("Model not loaded. Call load() first.")
        
        try:
            self.logger.info(f"Generating text for prompt: {prompt[:100]}...")
            
            # Prepare generation parameters
            generation_params = self._prepare_generation_params(**kwargs)
            
            # Make request to Ollama
            response = self._make_generation_request(prompt, generation_params)
            
            if not response or 'response' not in response:
                raise ModelError("No response generated from Ollama model")
            
            generated_text = response['response']
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
    
    def _check_ollama_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def _check_model_exists(self) -> bool:
        """Check if the model exists in Ollama."""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'] == self.model_name for model in models)
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error checking model existence: {e}")
            return False
    
    def _pull_model(self) -> None:
        """Pull the model from Ollama registry."""
        try:
            self.logger.info(f"Pulling model {self.model_name} from Ollama...")
            response = requests.post(
                f"{self.ollama_base_url}/api/pull",
                json={"name": self.model_name},
                stream=True,
                timeout=300  # 5 minutes timeout for model pull
            )
            
            if response.status_code != 200:
                raise ModelError(f"Failed to pull model: {response.text}")
            
            # Stream the response to show progress
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if 'status' in data:
                            self.logger.info(f"Pull status: {data['status']}")
                    except json.JSONDecodeError:
                        continue
            
            self.logger.info(f"Model {self.model_name} pulled successfully")
            
        except requests.exceptions.RequestException as e:
            raise ModelError(f"Failed to pull model: {str(e)}")
    
    def _test_model(self) -> None:
        """Test the model with a simple prompt."""
        try:
            test_prompt = "Hello, how are you?"
            generation_params = self._prepare_generation_params(max_length=10)
            response = self._make_generation_request(test_prompt, generation_params)
            
            if not response or 'response' not in response:
                raise ModelError("Model test failed - no response generated")
            
            self.logger.info("Model test successful")
            
        except Exception as e:
            raise ModelError(f"Model test failed: {str(e)}")
    
    def _prepare_generation_params(self, **kwargs) -> Dict[str, Any]:
        """Prepare generation parameters for Ollama."""
        # Map our config to Ollama parameters
        params = {
            "model": self.model_name,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', self.config.temperature),
                "top_p": kwargs.get('top_p', 0.9),
                "top_k": kwargs.get('top_k', 40),
                "repeat_penalty": kwargs.get('repetition_penalty', self.config.repetition_penalty),
                "num_predict": kwargs.get('max_length', self.config.max_length),
            }
        }
        
        # Add any extra parameters
        if 'stop' in kwargs:
            params['options']['stop'] = kwargs['stop']
        
        return params
    
    def _make_generation_request(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a generation request to Ollama."""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "prompt": prompt,
                    **params
                },
                timeout=60  # 1 minute timeout for generation
            )
            
            if response.status_code != 200:
                raise ModelError(f"Ollama API error: {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ModelError(f"Request failed: {str(e)}")
    
    def _create_task_template(self, instruction: str) -> str:
        """Create a structured task template."""
        return f"""You are a friendly chatbot assistant that gives structured output.
Your role is to arrange the given task in this structure.

### Instruction:
{instruction}

### Response:
"""
    
    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._model_loaded
    
    def unload(self) -> None:
        """Unload the model (Ollama keeps models in memory)."""
        self._model_loaded = False
        self.logger.info("Ollama model unloaded from memory")


# Global model instance (singleton pattern)
_ollama_model_instance: Optional[OllamaModel] = None


def get_ollama_model_instance() -> OllamaModel:
    """Get the global Ollama model instance (singleton)."""
    global _ollama_model_instance
    
    if _ollama_model_instance is None:
        settings = get_settings()
        _ollama_model_instance = OllamaModel(
            model_name=settings.model_name,
            device=settings.model_device,
            config=ModelConfig(
                max_length=settings.model_max_length,
                temperature=settings.model_temperature,
                repetition_penalty=settings.model_repetition_penalty
            )
        )
        _ollama_model_instance.load()
    
    return _ollama_model_instance


def check_ollama_models() -> List[Dict[str, Any]]:
    """Check available Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return response.json().get('models', [])
        return []
    except requests.exceptions.RequestException:
        return []


def is_ollama_running() -> bool:
    """Check if Ollama server is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
