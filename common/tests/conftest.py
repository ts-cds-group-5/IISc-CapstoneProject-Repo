"""Pytest configuration and fixtures for CCCP Advanced."""

import pytest
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from cccp.core.config import get_settings
from cccp.core.logging import setup_logging


@pytest.fixture(scope="session")
def settings():
    """Get application settings."""
    return get_settings()


@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Setup logging for tests."""
    setup_logging(level="DEBUG", log_to_file=False)


@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing."""
    return {
        "prompt": "What is 2 + 2?",
        "user_id": "test_user",
        "max_length": 256,
        "temperature": 0.2,
        "use_tools": True
    }


@pytest.fixture
def sample_tool_request():
    """Sample tool request for testing."""
    return {
        "tool_name": "multiply",
        "parameters": {"a": 5, "b": 3},
        "user_id": "test_user"
    }

