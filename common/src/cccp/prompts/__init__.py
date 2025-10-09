"""
Centralized prompt management for CCCP.

This module provides versioned prompts for various AI tasks.
"""

from .config import get_prompt, PromptConfig

__all__ = ['get_prompt', 'PromptConfig']

