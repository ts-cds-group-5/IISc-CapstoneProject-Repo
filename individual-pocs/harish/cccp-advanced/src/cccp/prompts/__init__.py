"""Prompt templates for CCCP Advanced."""

from .base import BasePromptTemplate, SystemPromptTemplate, UserPromptTemplate
from .math_prompts import MathPromptTemplates
from .message_handler import MessageHandler

__all__ = [
    "BasePromptTemplate",
    "SystemPromptTemplate", 
    "UserPromptTemplate",
    "MathPromptTemplates",
    "MessageHandler"
]
