"""Unit tests for models."""

import pytest
from unittest.mock import Mock, patch
from cccp.models.phi2_model import Phi2Model, ModelConfig
from cccp.core.exceptions import ModelError


class TestModelConfig:
    """Test ModelConfig class."""
    
    def test_model_config_creation(self):
        """Test creating a model config."""
        config = ModelConfig(
            max_length=512,
            temperature=0.5,
            repetition_penalty=1.1
        )
        
        assert config.max_length == 512
        assert config.temperature == 0.5
        assert config.repetition_penalty == 1.1
        assert config.do_sample is True
        assert config.truncation is True
    
    def test_model_config_to_dict(self):
        """Test converting config to dictionary."""
        config = ModelConfig(max_length=256, temperature=0.2)
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["max_length"] == 256
        assert config_dict["temperature"] == 0.2
        assert "do_sample" in config_dict
        assert "truncation" in config_dict


class TestPhi2Model:
    """Test Phi2Model class."""
    
    def test_phi2_model_creation(self):
        """Test creating a Phi2Model instance."""
        model = Phi2Model(
            model_name="test-model",
            device="cpu",
            config=ModelConfig(max_length=128)
        )
        
        assert model.model_name == "test-model"
        assert model.device == "cpu"
        assert model.config.max_length == 128
        assert not model.is_loaded
    
    @patch('cccp.models.phi2_model.AutoTokenizer')
    @patch('cccp.models.phi2_model.AutoModelForCausalLM')
    @patch('cccp.models.phi2_model.pipeline')
    def test_phi2_model_load(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test loading the Phi2Model."""
        # Mock the tokenizer and model
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.eos_token_id = 50256
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        mock_model_instance = Mock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Create and load model
        model = Phi2Model("test-model", "cpu")
        model.load()
        
        # Verify calls
        mock_tokenizer.from_pretrained.assert_called_once_with("test-model")
        mock_model.from_pretrained.assert_called_once()
        mock_pipeline.assert_called_once()
        
        assert model.is_loaded
    
    def test_phi2_model_generate_not_loaded(self):
        """Test generating text when model is not loaded."""
        model = Phi2Model("test-model", "cpu")
        
        with pytest.raises(ModelError, match="Model not loaded"):
            model.generate("test prompt")
    
    @patch('cccp.models.phi2_model.AutoTokenizer')
    @patch('cccp.models.phi2_model.AutoModelForCausalLM')
    @patch('cccp.models.phi2_model.pipeline')
    def test_phi2_model_generate(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test generating text with loaded model."""
        # Setup mocks
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.eos_token_id = 50256
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        mock_model_instance = Mock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.return_value = [{"generated_text": "Test response"}]
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Create, load, and test model
        model = Phi2Model("test-model", "cpu")
        model.load()
        
        result = model.generate("test prompt")
        assert result == "Test response"
    
    def test_phi2_model_create_task_template(self):
        """Test creating task template."""
        model = Phi2Model("test-model", "cpu")
        
        template = model._create_task_template("test instruction")
        
        assert "test instruction" in template
        assert "### instruction:" in template
        assert "Output:###Response:" in template

