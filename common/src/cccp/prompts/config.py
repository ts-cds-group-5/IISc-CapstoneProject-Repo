"""
Prompt configuration and version management.

This module allows easy switching between different prompt versions
and tracks which versions are being used for different tasks.
"""

from typing import Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PromptVersion(Enum):
    """Available prompt versions for different tasks."""
    # Tool Detection Versions
    TOOL_DETECTION_V1_BASIC = "tool_detection.v1_basic"
    TOOL_DETECTION_V2_LLAMA_OPTIMIZED = "tool_detection.v2_llama_optimized"
    TOOL_DETECTION_V3_ENHANCED = "tool_detection.v3_enhanced"
    
    # Add other prompt types here as needed
    # CHAT_V1 = "chat.v1"
    # SUMMARIZATION_V1 = "summarization.v1"


class PromptConfig:
    """
    Configuration for prompt versions.
    
    Modify ACTIVE_VERSIONS to switch between different prompt implementations.
    """
    
    # Configure which version to use for each task
    ACTIVE_VERSIONS = {
        "tool_detection": PromptVersion.TOOL_DETECTION_V2_LLAMA_OPTIMIZED,
        # Add other tasks here
        # "chat": PromptVersion.CHAT_V1,
    }
    
    # Metadata for tracking experiments
    PROMPT_METADATA = {
        PromptVersion.TOOL_DETECTION_V1_BASIC: {
            "description": "Basic LLM tool detection prompt",
            "best_for": "General purpose models",
            "tested_with": ["gpt-3.5", "gpt-4"],
            "avg_accuracy": None,  # Track performance metrics
        },
        PromptVersion.TOOL_DETECTION_V2_LLAMA_OPTIMIZED: {
            "description": "Llama 3.2 optimized with chat template",
            "best_for": "Llama 3.2 models",
            "tested_with": ["llama-3.2"],
            "avg_accuracy": None,
        },
        PromptVersion.TOOL_DETECTION_V3_ENHANCED: {
            "description": "Enhanced version with better JSON handling",
            "best_for": "Testing and experimentation",
            "tested_with": [],
            "avg_accuracy": None,
        },
    }
    
    @classmethod
    def get_active_version(cls, task: str) -> PromptVersion:
        """Get the currently active prompt version for a task."""
        version = cls.ACTIVE_VERSIONS.get(task)
        if not version:
            raise ValueError(f"No active version configured for task: {task}")
        logger.info(f"Using prompt version: {version.value} for task: {task}")
        return version
    
    @classmethod
    def get_metadata(cls, version: PromptVersion) -> Dict[str, Any]:
        """Get metadata for a specific prompt version."""
        return cls.PROMPT_METADATA.get(version, {})


def get_prompt(task: str, **kwargs) -> str:
    """
    Get the active prompt for a specific task.
    
    Args:
        task: The task type (e.g., "tool_detection")
        **kwargs: Additional parameters to pass to the prompt template
        
    Returns:
        Formatted prompt string
        
    Example:
        >>> prompt = get_prompt("tool_detection", 
        ...                     user_input="What's in my cart?",
        ...                     tools_info="Tool: getorder...")
    """
    version = PromptConfig.get_active_version(task)
    
    # Import the appropriate prompt module
    if version == PromptVersion.TOOL_DETECTION_V1_BASIC:
        from .tool_detection.v1_basic import get_tool_detection_prompt
        return get_tool_detection_prompt(**kwargs)
    
    elif version == PromptVersion.TOOL_DETECTION_V2_LLAMA_OPTIMIZED:
        from .tool_detection.v2_llama_optimized import get_tool_detection_prompt
        return get_tool_detection_prompt(**kwargs)
    
    elif version == PromptVersion.TOOL_DETECTION_V3_ENHANCED:
        from .tool_detection.v3_enhanced import get_tool_detection_prompt
        return get_tool_detection_prompt(**kwargs)
    
    else:
        raise ValueError(f"Prompt version not implemented: {version}")

