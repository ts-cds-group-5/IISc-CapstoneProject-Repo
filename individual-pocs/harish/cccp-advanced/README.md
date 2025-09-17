# CCCP Advanced

**Advanced Conversational Chatbot with LangGraph and MCP Server**

A modern, scalable conversational AI system built with FastAPI, LangGraph, and MCP (Model Context Protocol) server capabilities.

## 🚀 Features

- **🤖 Conversational AI**: Powered by Microsoft Phi-2 model
- **🔧 Tool Integration**: Built-in math tools and extensible tool system
- **🌐 Modern API**: FastAPI-based REST API with automatic documentation
- **💬 Web UI**: Beautiful Streamlit interface
- **🔄 LangGraph Integration**: Advanced workflow management (coming soon)
- **🔌 MCP Server**: Model Context Protocol support (coming soon)
- **📊 Comprehensive Logging**: Structured logging with multiple levels
- **🧪 Testing**: Full test suite with pytest
- **📚 Documentation**: Comprehensive docs and examples

## 🏗️ Architecture

```
cccp-advanced/
├── src/cccp/                    # Main source code
│   ├── api/                     # FastAPI application
│   │   ├── routes/              # API endpoints
│   │   └── models/              # Request/Response models
│   ├── core/                    # Core functionality
│   │   ├── config.py            # Configuration management
│   │   ├── logging.py           # Logging setup
│   │   └── exceptions.py        # Custom exceptions
│   ├── models/                  # ML models
│   │   └── phi2_model.py        # Phi-2 model implementation
│   ├── services/                # Business logic
│   │   ├── chat_service.py      # Chat operations
│   │   └── model_service.py     # Model management
│   ├── ui/                      # User interface
│   │   └── streamlit_app.py     # Streamlit UI
│   ├── agents/                  # LangGraph agents (coming soon)
│   ├── tools/                   # MCP tools (coming soon)
│   └── mcp/                     # MCP server (coming soon)
├── tests/                       # Test suite
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
└── config/                      # Configuration files
```

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- pip or uv package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cccp-advanced
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   # Or for development:
   pip install -e ".[dev]"
   ```

4. **Start the server**
   ```bash
   python scripts/start_server.py
   ```

5. **Start the UI** (in another terminal)
   ```bash
   python scripts/start_ui.py
   ```

### Using uv (Recommended)

```bash
# Install uv if you haven't already
pip install uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## 🚀 Usage

### API Server

Start the FastAPI server:

```bash
python scripts/start_server.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Web UI

Start the Streamlit UI:

```bash
python scripts/start_ui.py
```

The UI will be available at: http://localhost:8501

### API Examples

#### Chat with the model

```bash
curl -X POST "http://localhost:8000/api/v1/chat/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "What is 5 + 3?",
       "user_id": "user123"
     }'
```

#### Use tools directly

```bash
curl -X POST "http://localhost:8000/api/v1/tools/multiply" \
     -H "Content-Type: application/json" \
     -d '{
       "tool_name": "multiply",
       "parameters": {"a": 5, "b": 3}
     }'
```

## ⚙️ Configuration

Configuration is managed through environment variables or a `.env` file:

```bash
# Application
DEBUG=false
ENVIRONMENT=development

# API
API_HOST=localhost
API_PORT=8000

# Model
MODEL_NAME=llama3.2:latest
MODEL_TYPE=phi2
MODEL_DEVICE=cpu
MODEL_MAX_LENGTH=256
MODEL_TEMPERATURE=0.2

# Ollama (if using Ollama models)
OLLAMA_BASE_URL=http://localhost:11434

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=false
```

## 🤖 Model Switching

CCCP Advanced supports multiple language models. You can easily switch between them by modifying the configuration.

### Supported Models

1. **Phi-2** (Microsoft) - Default, lightweight model
2. **Ollama Models** - Local models like Llama 3.2, CodeLlama, etc.
3. **Auto-detection** - Automatically chooses the best available model

### Quick Model Switching

#### Option 1: Using Environment Variables

Create a `.env` file from the example:
```bash
cp env.example .env
```

Then modify the model settings in `.env`:

**To use Phi-2:**
```bash
# MODEL_NAME=microsoft/phi-2  # Uncomment this line
MODEL_NAME=llama3.2:latest    # Comment out this line
MODEL_TYPE=phi2
```

**To use Ollama (Llama 3.2):**
```bash
MODEL_NAME=llama3.2:latest
MODEL_TYPE=ollama
```

**To use Auto-detection:**
```bash
MODEL_NAME=llama3.2:latest
# MODEL_TYPE=auto  # Uncomment this line
MODEL_TYPE=phi2    # Comment out this line
```

#### Option 2: Using Configuration Files

Edit `src/cccp/core/config.py`:

**To use Phi-2:**
```python
# model_name: str = Field(default="microsoft/phi-2", env="MODEL_NAME")  # Uncomment
model_name: str = Field(default="llama3.2:latest", env="MODEL_NAME")    # Comment out
model_type: str = Field(default="phi2", env="MODEL_TYPE")
```

**To use Ollama:**
```python
model_name: str = Field(default="llama3.2:latest", env="MODEL_NAME")
model_type: str = Field(default="ollama", env="MODEL_TYPE")
```

**To use Auto-detection:**
```python
model_name: str = Field(default="llama3.2:latest", env="MODEL_NAME")
# model_type: str = Field(default="auto", env="MODEL_TYPE")  # Uncomment
model_type: str = Field(default="phi2", env="MODEL_TYPE")    # Comment out
```

### Setting Up Ollama

If you want to use Ollama models:

1. **Install Ollama:**
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # Download from https://ollama.ai/download
   ```

2. **Start Ollama service:**
   ```bash
   ollama serve
   ```

3. **Pull a model:**
   ```bash
   ollama pull llama3.2:latest
   # or
   ollama pull codellama:latest
   # or
   ollama pull mistral:latest
   ```

4. **Configure CCCP to use Ollama:**
   ```bash
   # In your .env file
   MODEL_NAME=llama3.2:latest
   MODEL_TYPE=ollama
   ```

### Model Comparison

| Model | Type | Size | Speed | Quality | Use Case |
|-------|------|------|-------|---------|----------|
| Phi-2 | Local | ~2.7GB | Fast | Good | Development, Testing |
| Llama 3.2 | Local (Ollama) | ~2GB | Fast | Excellent | Production, General Use |
| CodeLlama | Local (Ollama) | ~3.8GB | Medium | Excellent | Code Generation |
| Mistral | Local (Ollama) | ~4.1GB | Medium | Excellent | General Use |

### Testing Your Model Setup

Use the built-in test script to verify your model configuration:

```bash
# Test Ollama integration
python test_ollama.py

# Test the full system
python run.py server
```

### Troubleshooting

**Ollama not working:**
- Ensure Ollama service is running: `ollama serve`
- Check if the model is pulled: `ollama list`
- Verify the model name in your configuration

**Phi-2 not loading:**
- Check internet connection (first download)
- Verify sufficient disk space (~3GB)
- Check Python dependencies are installed

**Auto-detection issues:**
- Ensure at least one model type is properly configured
- Check logs for specific error messages

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cccp

# Run specific test categories
pytest -m unit
pytest -m integration
```

## 📚 Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Security check
bandit -r src/
safety check
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pre-commit install
```

## 🔧 Available Tools

- **multiply**: Multiply two numbers
- **add**: Add two numbers
- **subtract**: Subtract two numbers

## 📖 API Documentation

### Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/v1/chat/generate` - Generate chat response
- `POST /api/v1/tools/multiply` - Execute multiply tool
- `GET /api/v1/tools/` - List available tools

### Models

#### ChatRequest
```json
{
  "prompt": "string",
  "user_id": "string",
  "max_length": 256,
  "temperature": 0.2,
  "use_tools": true
}
```

#### ChatResponse
```json
{
  "response": "string",
  "status": "success",
  "user_id": "string",
  "tool_used": "multiply",
  "metadata": {}
}
```

## 🚧 Roadmap

- [ ] **LangGraph Integration**: Advanced workflow management
- [ ] **MCP Server**: Model Context Protocol support
- [ ] **Additional Models**: Support for more language models
- [ ] **Database Integration**: Persistent storage
- [ ] **Authentication**: User management and security
- [ ] **Monitoring**: Metrics and observability
- [ ] **Docker Support**: Containerized deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Microsoft for the Phi-2 model
- FastAPI team for the excellent framework
- Streamlit team for the UI framework
- LangChain team for the AI framework
- The open-source community

## 📞 Support

For questions and support, please open an issue on GitHub.

---

**Made with ❤️ by the CCCP Advanced team**

