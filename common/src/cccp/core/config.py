"""Configuration management for CCCP Advanced."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

try:
    from pydantic import BaseSettings, Field
except ImportError:
    from pydantic_settings import BaseSettings
    from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "CCCP Advanced"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API
    api_host: str = Field(default="localhost", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    
    # Model
    #model_name: str = Field(default="microsoft/phi-2", env="MODEL_NAME")  # Uncomment to use Phi2
    #model_type: str = Field(default="phi2", env="MODEL_TYPE")

    model_name: str = Field(default="llama3.2:latest", env="MODEL_NAME")
    model_type: str = Field(default="auto", env="MODEL_TYPE")  # Uncomment to enable auto-detection
    
    model_device: str = Field(default="cpu", env="MODEL_DEVICE")
    model_max_length: int = Field(default=512, env="MODEL_MAX_LENGTH")
    model_temperature: float = Field(default=0.2, env="MODEL_TEMPERATURE")
    model_repetition_penalty: float = Field(default=1.2, env="MODEL_REPETITION_PENALTY")
    
    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_to_file: bool = Field(default=False, env="LOG_TO_FILE")
    log_file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    
    # MCP Server
    mcp_host: str = Field(default="localhost", env="MCP_HOST")
    mcp_port: int = Field(default=8001, env="MCP_PORT")
    mcp_tools: str = Field(default="math,file", env="MCP_TOOLS")
    #mcp_tools: list[str] = Field(default=["math", "file"], env="MCP_TOOLS")
    
    # LangGraph
    langgraph_debug: bool = Field(default=False, env="LANGGRAPH_DEBUG")
    max_iterations: int = Field(default=10, env="MAX_ITERATIONS")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    #cors_origins: list[str] = Field(default=["*"], env="CORS_ORIGINS")

    
    # Database (for future use)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    # PostgreSQL MCP
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="postgres", env="POSTGRES_DB")
    mcp_postgres_enabled: bool = Field(default=True, env="MCP_POSTGRES_ENABLED")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent


def get_config_dir() -> Path:
    """Get the configuration directory."""
    return get_project_root() / "config"


def get_logs_dir() -> Path:
    """Get the logs directory."""
    logs_dir = get_project_root() / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir
