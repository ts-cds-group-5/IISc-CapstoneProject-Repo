# Prompt Management System

This directory contains a centralized, versioned prompt management system for CCCP.

## 📁 Structure

```
prompts/
├── __init__.py                 # Main exports
├── config.py                   # Version configuration
├── README.md                   # This file
└── tool_detection/             # Tool detection prompts
    ├── __init__.py
    ├── v1_basic.py            # Basic LLM prompt
    ├── v2_llama_optimized.py  # Llama 3.2 optimized
    └── v3_enhanced.py         # Experimental version
```

## 🎯 Purpose

This system allows you to:
- ✅ **Version control** different prompt implementations
- ✅ **A/B test** prompt effectiveness
- ✅ **Track performance** metrics for each version
- ✅ **Quick switching** between versions
- ✅ **Easy rollback** if a new prompt performs poorly

## 🚀 Usage

### Basic Usage

```python
from cccp.prompts import get_prompt

# Get the active prompt for tool detection
prompt = get_prompt(
    "tool_detection",
    user_input="What happened to my order 2?",
    tools_info="Tool: getorder\nDescription: Get order status..."
)
```

### Switching Versions

Edit `config.py` to change which version is active:

```python
# In config.py
ACTIVE_VERSIONS = {
    "tool_detection": PromptVersion.TOOL_DETECTION_V2_LLAMA_OPTIMIZED,
    # Change to:
    # "tool_detection": PromptVersion.TOOL_DETECTION_V1_BASIC,
}
```

### Getting Metadata

```python
from cccp.prompts import PromptConfig
from cccp.prompts.config import PromptVersion

metadata = PromptConfig.get_metadata(
    PromptVersion.TOOL_DETECTION_V2_LLAMA_OPTIMIZED
)
print(metadata)
# {
#     "description": "Llama 3.2 optimized with chat template",
#     "best_for": "Llama 3.2 models",
#     "tested_with": ["llama-3.2"],
#     "avg_accuracy": None
# }
```

## 📝 Available Prompt Versions

### Tool Detection

| Version | Description | Best For | Status |
|---------|-------------|----------|--------|
| `v1_basic` | Basic LLM prompt | General purpose models | Stable |
| `v2_llama_optimized` | Llama chat template | Llama 3.2 | **Active** |
| `v3_enhanced` | Experimental | Testing | Experimental |

## 🔧 Creating a New Prompt Version

### Step 1: Create New Version File

```bash
# Create new version file
touch src/cccp/prompts/tool_detection/v4_my_version.py
```

### Step 2: Implement the Prompt

```python
# v4_my_version.py
"""
Version 4: My Custom Prompt

Description of what makes this version unique.

Performance Notes:
- Tested with: [model names]
- Average accuracy: TBD
- Best use case: [description]
"""

def get_tool_detection_prompt(user_input: str, tools_info: str) -> str:
    """Generate the tool detection prompt."""
    prompt = f"""Your custom prompt here...
    
User Query: {user_input}

Available Tools:
{tools_info}
"""
    return prompt

# Optional: Recommended parameters
RECOMMENDED_PARAMS = {
    "temperature": 0.1,
    "max_tokens": 200,
}
```

### Step 3: Register in Config

Add to `config.py`:

```python
class PromptVersion(Enum):
    # ... existing versions ...
    TOOL_DETECTION_V4_MY_VERSION = "tool_detection.v4_my_version"

# Add metadata
PROMPT_METADATA = {
    # ... existing metadata ...
    PromptVersion.TOOL_DETECTION_V4_MY_VERSION: {
        "description": "My custom version",
        "best_for": "Specific use case",
        "tested_with": ["model-name"],
        "avg_accuracy": None,
    },
}

# Add to get_prompt function
def get_prompt(task: str, **kwargs) -> str:
    # ... existing code ...
    elif version == PromptVersion.TOOL_DETECTION_V4_MY_VERSION:
        from .tool_detection.v4_my_version import get_tool_detection_prompt
        return get_tool_detection_prompt(**kwargs)
```

### Step 4: Activate Your Version

```python
ACTIVE_VERSIONS = {
    "tool_detection": PromptVersion.TOOL_DETECTION_V4_MY_VERSION,
}
```

## 🧪 Testing Different Versions

### Approach 1: Manual Testing

```python
# Test v1
from cccp.prompts.tool_detection.v1_basic import get_tool_detection_prompt as v1_prompt
prompt_v1 = v1_prompt(user_input="test", tools_info="tools")

# Test v2
from cccp.prompts.tool_detection.v2_llama_optimized import get_tool_detection_prompt as v2_prompt
prompt_v2 = v2_prompt(user_input="test", tools_info="tools")

# Compare outputs
```

### Approach 2: Automated Comparison

Create a test script to compare versions:

```python
# test_prompts.py
from cccp.prompts import get_prompt, PromptConfig
from cccp.prompts.config import PromptVersion

test_cases = [
    "What happened to my order 2?",
    "Multiply 5 and 3",
    "Hello there",
]

for version in [PromptVersion.TOOL_DETECTION_V1_BASIC, 
                PromptVersion.TOOL_DETECTION_V2_LLAMA_OPTIMIZED]:
    print(f"\n=== Testing {version.value} ===")
    for test in test_cases:
        # Change active version temporarily
        PromptConfig.ACTIVE_VERSIONS["tool_detection"] = version
        prompt = get_prompt("tool_detection", user_input=test, tools_info="...")
        # Test with your model...
```

## 📊 Tracking Performance

Update metadata with performance metrics:

```python
# After testing a version
PROMPT_METADATA = {
    PromptVersion.TOOL_DETECTION_V2_LLAMA_OPTIMIZED: {
        "description": "Llama 3.2 optimized",
        "best_for": "Llama 3.2 models",
        "tested_with": ["llama-3.2"],
        "avg_accuracy": 0.92,  # Update with actual results
        "test_date": "2025-10-09",
        "test_samples": 100,
    },
}
```

## 🎨 Best Practices

1. **Document Everything**: Add detailed performance notes to each version
2. **Test Thoroughly**: Run multiple test cases before promoting to active
3. **Keep Stable Versions**: Don't delete working versions
4. **Use v3_enhanced**: Use v3 as experimental playground
5. **Track Metrics**: Record accuracy, latency, and other metrics
6. **Version Naming**: Use clear, descriptive version names

## 🔄 Migration Path

When migrating from hardcoded prompts:

```python
# Old way (hardcoded in agent)
prompt = f"You are a tool detector... {user_input}"

# New way (centralized)
from cccp.prompts import get_prompt

prompt = get_prompt(
    "tool_detection",
    user_input=user_input,
    tools_info=self._get_tools_info()
)
```

## 🚨 Troubleshooting

### Issue: Import errors

```python
# Make sure __init__.py files exist in all directories
# Check that you're importing from the correct path
from cccp.prompts import get_prompt  # Correct
```

### Issue: Version not found

```python
# Ensure version is registered in config.py
# Check that the version enum exists
# Verify the version is added to get_prompt() function
```

### Issue: Prompt not working as expected

```python
# Test the raw prompt output first
prompt = get_prompt("tool_detection", ...)
print(prompt)  # Inspect the actual prompt

# Try a different version
PromptConfig.ACTIVE_VERSIONS["tool_detection"] = PromptVersion.TOOL_DETECTION_V1_BASIC
```

## 🎓 Example: Complete Workflow

```python
# 1. Create new experimental prompt in v3_enhanced.py
# 2. Test it manually
from cccp.prompts.tool_detection.v3_enhanced import get_tool_detection_prompt
test_prompt = get_tool_detection_prompt("test query", "tools info")

# 3. If it works well, activate it
from cccp.prompts.config import PromptConfig, PromptVersion
PromptConfig.ACTIVE_VERSIONS["tool_detection"] = PromptVersion.TOOL_DETECTION_V3_ENHANCED

# 4. Test in production
# 5. Track performance metrics
# 6. If successful, promote to v4 stable version
```

## 📚 Future Enhancements

- [ ] Automatic A/B testing framework
- [ ] Performance metric tracking database
- [ ] Prompt template inheritance
- [ ] Multi-language prompt support
- [ ] Automatic prompt optimization using feedback

