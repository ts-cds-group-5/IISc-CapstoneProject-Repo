#!/usr/bin/env python3
"""Test script for Ollama integration."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from cccp.models.ollama_model import OllamaModel, is_ollama_running, check_ollama_models
from cccp.core.logging import setup_logging, get_logger

def main():
    """Test Ollama integration."""
    setup_logging()
    logger = get_logger(__name__)
    
    print("🔍 Testing Ollama Integration")
    print("=" * 50)
    
    # Check if Ollama is running
    print("\n1. Checking if Ollama is running...")
    if is_ollama_running():
        print("✅ Ollama is running!")
    else:
        print("❌ Ollama is not running. Please start Ollama first:")
        print("   ollama serve")
        return
    
    # Check available models
    print("\n2. Checking available models...")
    models = check_ollama_models()
    if models:
        print("✅ Available models:")
        for model in models:
            print(f"   - {model['name']}")
    else:
        print("❌ No models found")
        return
    
    # Test model loading
    print("\n3. Testing model loading...")
    try:
        model = OllamaModel(model_name="llama3.2:latest")
        model.load()
        print("✅ Model loaded successfully!")
        
        # Test generation
        print("\n4. Testing text generation...")
        test_prompt = "Hello! How are you today?"
        response = model.generate(test_prompt)
        print(f"✅ Generated response: {response}")
        
        # Test with template
        print("\n5. Testing template generation...")
        template_response = model.generate_with_prompt_template("Tell me a joke")
        print(f"✅ Template response: {template_response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n🎉 All tests passed! Ollama integration is working correctly.")

if __name__ == "__main__":
    main()
