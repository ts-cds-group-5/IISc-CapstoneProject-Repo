"""Math-specific prompt templates with few-shot examples."""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from .base import BasePromptTemplate

class MathPromptTemplates:
    """Math-specific prompt templates with few-shot examples."""
    
    # Few-shot examples for math tools
    MATH_FEW_SHOT_EXAMPLES = [
        {
            "input": "What is 5 + 3?",
            "output": "I'll add 5 and 3 for you.\n\n<tool_call>\n<tool_name>add</tool_name>\n<parameters>\n<parameter name=\"a\">5</parameter>\n<parameter name=\"b\">3</parameter>\n</parameters>\n</tool_call>\n\nThe result of adding 5 and 3 is 8."
        },
        {
            "input": "Calculate 7 * 4",
            "output": "I'll multiply 7 and 4 for you.\n\n<tool_call>\n<tool_name>multiply</tool_name>\n<parameters>\n<parameter name=\"a\">7</parameter>\n<parameter name=\"b\">4</parameter>\n</parameters>\n</tool_call>\n\nThe result of multiplying 7 and 4 is 28."
        },
        {
            "input": "What's 12 + 8?",
            "output": "I'll add 12 and 8 for you.\n\n<tool_call>\n<tool_name>add</tool_name>\n<parameters>\n<parameter name=\"a\">12</parameter>\n<parameter name=\"b\">8</parameter>\n</parameters>\n</tool_call>\n\nThe result of adding 12 and 8 is 20."
        }
    ]
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get the system prompt for math operations."""
        return """You are a helpful math assistant. You have access to mathematical tools to perform calculations.

Available tools:
- add: Add two integers (returns a*a + b*b - this is a special "squared add" operation)
- multiply: Multiply two integers

When a user asks for a mathematical calculation:
1. Identify the operation needed
2. Extract the numbers from the user's input
3. Use the appropriate tool to perform the calculation
4. Present the result clearly to the user

Always use the tools for mathematical operations rather than trying to calculate manually."""

    @classmethod
    def get_chat_prompt_template(cls) -> ChatPromptTemplate:
        """Get the complete chat prompt template with few-shot examples."""
        
        # Create few-shot example template
        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("ai", "{output}")
        ])
        
        # Create few-shot prompt
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=cls.MATH_FEW_SHOT_EXAMPLES
        )
        
        # Create the main chat prompt template
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", cls.get_system_prompt()),
            few_shot_prompt,
            ("human", "{user_input}"),
            ("assistant", "{response}")
        ])
        
        return chat_prompt
    
    @classmethod
    def format_math_messages(cls, user_input: str, response: str = "") -> List[BaseMessage]:
        """Format messages for math operations."""
        template = cls.get_chat_prompt_template()
        return template.format_messages(
            user_input=user_input,
            response=response
        )
