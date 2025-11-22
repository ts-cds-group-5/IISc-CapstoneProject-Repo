# Troubleshooting Catalog Tools

**Last Updated:** October 10, 2025

---

## Common Issues and Solutions

### Issue 1: JSON Parsing Error - "Extra data: line 1 column 3"

**Symptoms:**
```
JSON validation failed: Extra data: line 1 column 3 (char 2)
LLM tool detection failed, falling back to regex
```

**Cause:** Llama 3.2 sometimes generates extra text before or after the JSON object.

**Solution:** ✅ **FIXED** - Improved JSON parsing in `custom_tool_calling_agent.py`
- Now properly extracts the first complete JSON object
- Handles nested braces correctly
- Logs raw response for debugging

**Test:** Ask "what collections do you have?" and check logs for successful JSON parsing.

---

### Issue 2: Tools Not Detected by LLM

**Symptoms:** User asks catalog question, but gets general chat response instead of catalog results.

**Debugging Steps:**

1. **Check tool registration:**
   ```bash
   python test_catalog_registration.py
   ```
   Should show all 3 catalog tools registered.

2. **Check LLM response in logs:**
   Look for lines like:
   ```
   Raw LLM response (first 200 chars): ...
   Extracted JSON string: ...
   Successfully parsed JSON: {'tool_name': 'listcollections', ...}
   ```

3. **Verify prompt version:**
   Should use `tool_detection.v2_llama_optimized`

4. **Check model temperature:**
   Lower temperature (0.1-0.2) gives more consistent tool detection

**Solutions:**

a) **If JSON parsing fails:**
   - Check logs for "Raw LLM response" to see what Llama generated
   - The improved parser should handle most cases
   - If it still fails, the prompt might need adjustment

b) **If wrong tool detected:**
   - Check tool descriptions are clear
   - Add more examples to `v2_llama_optimized.py`
   - Adjust model temperature

c) **If no tool detected (null):**
   - User query might be too vague
   - Try rephrasing query to be more specific
   - Check if query keywords match tool descriptions

---

### Issue 3: Database Connection Errors

**Symptoms:**
```
ToolError: Database error: ...
```

**Solutions:**

1. **Check Docker Postgres is running:**
   ```bash
   docker ps | grep postgres
   ```

2. **Check environment variables:**
   ```bash
   echo $POSTGRES_HOST
   echo $POSTGRES_PORT
   echo $POSTGRES_USER
   ```

3. **Test database connection:**
   ```bash
   psql -h localhost -U postgres -d postgres
   ```

4. **Check MCP server is accessible:**
   ```bash
   ps aux | grep mcp_server
   ```

---

### Issue 4: Empty Results from Database

**Symptoms:** Tool executes but returns "No products found" or "No collections found"

**Solutions:**

1. **Verify sample data is loaded:**
   ```sql
   SELECT COUNT(*) FROM collection;  -- Should be 4
   SELECT COUNT(*) FROM g5_product;  -- Should be 24
   ```

2. **If data missing, load from README-docker.md:**
   ```bash
   # Follow the SQL commands in README-docker.md lines 60-213
   psql -h localhost -U postgres -d postgres -f load_sample_data.sql
   ```

3. **Check filters aren't too restrictive:**
   - Try without filters first
   - Check price ranges are reasonable
   - Verify collection names match exactly

---

### Issue 5: Tool Registered But Not Working

**Symptoms:** Tool shows in registry but errors when executed

**Debugging:**

1. **Test tool directly:**
   ```python
   from cccp.tools.catalog.list_collections import ListCollectionsTool
   
   tool = ListCollectionsTool()
   result = tool.run()
   print(result)
   ```

2. **Check logs for specific error:**
   ```bash
   # Enable DEBUG logging
   export LOG_LEVEL=DEBUG
   ```

3. **Common issues:**
   - Missing database connection
   - Incorrect SQL syntax
   - Missing table or column
   - Permission issues

---

## Logging Guide

### Enable Debug Logging

**Option 1: Environment Variable**
```bash
export LOG_LEVEL=DEBUG
```

**Option 2: In Code**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Key Log Messages to Watch

**Tool Detection:**
```
INFO - Processing user input: what collections do you have?
INFO - Using prompt version: tool_detection.v2_llama_optimized
DEBUG - Raw LLM response (first 200 chars): ...
DEBUG - Extracted JSON string: {"tool_name": "listcollections", ...}
INFO - Successfully parsed JSON: {'tool_name': 'listcollections', ...}
```

**Tool Execution:**
```
INFO - ListCollectionsTool: Fetching collections from database
DEBUG - ListCollectionsTool: MCP client connected
DEBUG - ListCollectionsTool: Executing query
INFO - ListCollectionsTool: Query returned 4 rows
DEBUG - ListCollectionsTool: MCP client closed
```

**Errors:**
```
ERROR - JSON validation failed: ...
ERROR - ListCollectionsTool: Database fetch error - ...
ERROR - Tool error in get_catalog: ...
```

---

## Testing Checklist

Before reporting an issue, verify:

- [ ] Virtual environment activated
- [ ] Docker Postgres running
- [ ] Database has sample data loaded
- [ ] Tools registered (run `test_catalog_registration.py`)
- [ ] No linting errors in catalog tools
- [ ] Environment variables set correctly
- [ ] Ollama/Llama 3.2 model accessible
- [ ] Logs show tool detection attempt
- [ ] MCP server accessible

---

## Quick Fixes

### Reset Everything
```bash
# Stop all services
docker-compose down

# Restart database
docker-compose up -d

# Reload sample data
psql -h localhost -U postgres -d postgres < load_sample_data.sql

# Restart Python environment
deactivate
cd /Users/achappa/devhak/gfc
source uv3135b/bin/activate
cd common

# Test registration
python test_catalog_registration.py
```

### Force Reload Tools
```python
# In Python console or script
import importlib
import sys

# Remove cached modules
for module in list(sys.modules.keys()):
    if 'cccp.tools.catalog' in module:
        del sys.modules[module]

# Re-import
from cccp.tools.catalog.list_collections import ListCollectionsTool
from cccp.tools.catalog.get_catalog import GetCatalogTool
from cccp.tools.catalog.search_products import SearchProductsTool

# Verify
from cccp.tools.registry import get_all_tools
tools = get_all_tools()
print([t.name for t in tools])
```

---

## Getting Help

If issues persist:

1. **Check logs** with DEBUG level enabled
2. **Run verification script** to check setup
3. **Test tools directly** (not through LLM)
4. **Verify database** has sample data
5. **Review documentation** in `CATALOG_TOOLS_IMPLEMENTATION.md`

**Provide this information when asking for help:**
- Error message (full stack trace)
- Relevant log lines
- Output of `test_catalog_registration.py`
- Database query results (SELECT COUNT from tables)
- Environment (OS, Python version, package versions)

---

*Last updated: October 10, 2025*

