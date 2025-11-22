# Product Catalog Tools Implementation

**Date:** October 10, 2025  
**Status:** Phase 1 Complete ✅  
**Author:** CCCP Advanced System  
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Implementation Summary](#implementation-summary)
3. [Architecture](#architecture)
4. [Tools Created](#tools-created)
5. [Database Schema](#database-schema)
6. [Integration with Llama 3.2](#integration-with-llama-32)
7. [Testing Strategy](#testing-strategy)
8. [Usage Examples](#usage-examples)
9. [Phase 2 Planning](#phase-2-planning)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This document describes the implementation of the Product Catalog Tools system for the CCCP Advanced platform. The system enables users to query product information, browse collections, and search for products using natural language through an LLM-powered interface.

### Goals

- ✅ Enable natural language queries for product catalogs
- ✅ Support collection browsing and product search
- ✅ Integrate with existing Llama 3.2 LLM system
- ✅ Use PostgreSQL database with MCP client
- ✅ Provide human-friendly formatted responses
- ✅ Prepare foundation for order placement (Phase 2)

### User Queries Supported

1. **"What collections do you have?"**
2. **"Show me your catalog"**
3. **"What products are in Electronics?"**
4. **"Find laptops under 50000"**
5. **"Show me products with 'Samsung'"**

---

## Implementation Summary

### Files Created

**Catalog Tools (5 files):**
```
src/cccp/tools/catalog/
├── __init__.py                  # Package initialization
├── list_collections.py          # ListCollectionsTool
├── get_catalog.py              # GetCatalogTool
├── search_products.py          # SearchProductsTool
└── catalog_utils.py            # Shared utility functions
```

**Order Tool Stub (1 file):**
```
src/cccp/tools/order/
└── place_order.py              # PlaceOrderTool (Phase 2 stub)
```

**Tests (2 files):**
```
tests/
├── unit/
│   └── test_catalog_tools.py          # Unit tests with mocks
└── integration/
    └── test_catalog_integration.py    # Integration tests with real DB
```

**Updated Files (2 files):**
- `src/cccp/agents/intent_classifier.py` - Added `catalog_inquiry` intent
- `src/cccp/prompts/tool_detection/v2_llama_optimized.py` - Added catalog examples

### Statistics

- **Total Lines of Code:** ~1,600
- **Tools Implemented:** 3 (+ 1 stub)
- **Test Cases:** 30+ unit tests, 15+ integration tests
- **Database Tables Used:** 2 (collection, g5_product)

---

## Architecture

### System Flow

```
User Query → Llama 3.2 LLM → Intent Classification → Tool Selection → Tool Execution → DB Query → Formatted Response
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                            │
│              (Streamlit / API / Chat)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              CustomToolCallingAgent                          │
│     (Llama 3.2 with v2_llama_optimized prompt)              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Intent Classifier                               │
│         (catalog_inquiry detection)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Tool Registry                                   │
│       (Auto-discovers BaseCCCPTool subclasses)              │
└────────┬────────┬────────┬───────────────────────────────────┘
         │        │        │
         ▼        ▼        ▼
    ┌────────┬────────┬────────┐
    │ List   │  Get   │Search  │
    │Collect │Catalog │Products│
    └────┬───┴────┬───┴────┬───┘
         │        │        │
         └────────┼────────┘
                  │
                  ▼
        ┌──────────────────┐
        │  MCP Postgres    │
        │     Client       │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │   PostgreSQL DB  │
        │  (Docker)        │
        └──────────────────┘
```

---

## Tools Created

### 1. ListCollectionsTool

**Purpose:** Lists all product collections with product counts

**Tool Name:** `listcollections`

**Parameters:** None

**SQL Query:**
```sql
SELECT
    c.collection_id,
    c.name AS collection_name,
    c.code AS collection_code,
    COUNT(p.product_id) AS product_count
FROM public.collection c
LEFT JOIN public.g5_product p
    ON p.collection_id = c.collection_id
GROUP BY c.collection_id, c.name, c.code
ORDER BY c.collection_id
```

**Example Response:**
```
🛍️  **Available Collections:**

📦 **Electronics** (COLL_ELEC)
   └─ 6 products
📦 **Furniture** (COLL_FURN)
   └─ 6 products
📦 **Books** (COLL_BOOK)
   └─ 6 products
📦 **Clothing** (COLL_CLOTH)
   └─ 6 products

✨ Total: 4 collections with 24 products
```

**Logging:**
- INFO: Query execution start/completion
- DEBUG: MCP connection lifecycle
- ERROR: DB errors with stack traces

---

### 2. GetCatalogTool

**Purpose:** Retrieves product catalog with optional filters

**Tool Name:** `getcatalog`

**Parameters:**
- `collection_name` (Optional[str]): Filter by collection
- `min_price` (Optional[float]): Minimum price filter
- `max_price` (Optional[float]): Maximum price filter
- `in_stock_only` (bool): Only show in-stock items (default: True)

**Dynamic SQL Building:**
```python
base_query = """
    SELECT c.collection_id, c.name AS collection_name,
           p.product_id, p.product_name, p.product_description,
           p.currency, p.product_price, p.product_stock_qty
    FROM public.g5_product p
    JOIN public.collection c ON c.collection_id = p.collection_id
"""
# WHERE clauses built dynamically based on filters
```

**Example Usage:**
```python
# Get all products
result = tool.run()

# Get Electronics only
result = tool.run(collection_name="Electronics")

# Get products under ₹10,000
result = tool.run(max_price=10000.0)

# Get Electronics products ₹5,000-₹20,000
result = tool.run(
    collection_name="Electronics",
    min_price=5000.0,
    max_price=20000.0
)
```

**Example Response:**
```
📋 **Product Catalog** (6 products)

📦 **Electronics** (6 products)
============================================================

• **Samsung Galaxy M35 5G (6GB/128GB)**
  Price: ₹ 16,999.00
  Stock: 60 available
  Brand: Samsung | 6.6" sAMOLED, Exynos chipset, 50MP triple cam, 6000mAh

• **Lenovo IdeaPad Slim 3 (Ryzen 5, 16GB/512GB)**
  Price: ₹ 52,990.00
  Stock: 25 available
  Brand: Lenovo | 15.6" FHD, Ryzen 5 5500U, Windows 11, MS Office
...
```

---

### 3. SearchProductsTool

**Purpose:** Searches products by keyword with optional filters

**Tool Name:** `searchproducts`

**Parameters:**
- `keyword` (str): **Required** - Search term for product names/descriptions
- `collection_name` (Optional[str]): Filter by collection
- `min_price` (Optional[float]): Minimum price filter
- `max_price` (Optional[float]): Maximum price filter
- `in_stock_only` (bool): Only show in-stock items (default: True)

**Search Logic:**
```sql
WHERE (p.product_name ILIKE '%keyword%' 
    OR p.product_description ILIKE '%keyword%')
```

**Example Usage:**
```python
# Search for "laptop"
result = tool.run(keyword="laptop")

# Search for "Samsung" in Electronics
result = tool.run(keyword="Samsung", collection_name="Electronics")

# Search for chairs under ₹10,000 in Furniture
result = tool.run(
    keyword="chair",
    collection_name="Furniture",
    max_price=10000.0
)
```

**Example Response:**
```
Found 1 product matching 'laptop' in Electronics.

📋 **Product Catalog** (1 product)

📦 **Electronics** (1 product)
============================================================

• **Lenovo IdeaPad Slim 3 (Ryzen 5, 16GB/512GB)**
  Price: ₹ 52,990.00
  Stock: 25 available
  Brand: Lenovo | 15.6" FHD, Ryzen 5 5500U, Windows 11, MS Office
```

---

### 4. PlaceOrderTool (Phase 2 Stub)

**Status:** 🚧 Stub - Awaiting Phase 2 implementation

**Purpose:** Place orders with synthetic payment processing

**Planned Workflow:**
1. Validate user registration
2. Check product stock availability
3. Create order record
4. Process synthetic payment
5. Update inventory
6. Generate order confirmation

**Database Tables Required:**
- `g5_customer` - User registration
- `g5_order` - Order records
- `g5_order_item` - Order line items
- `g5_payment` - Payment records

See `src/cccp/tools/order/place_order.py` for detailed implementation plan.

---

## Database Schema

### Tables Used

#### 1. collection

```sql
CREATE TABLE IF NOT EXISTS public.collection (
    collection_id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    uuid uuid NOT NULL DEFAULT gen_random_uuid(),
    name character varying NOT NULL,
    description text,
    code character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT collection_pkey PRIMARY KEY (collection_id),
    CONSTRAINT "COLLECTION_CODE_UNIQUE" UNIQUE (code),
    CONSTRAINT "COLLECTION_UUID_UNIQUE" UNIQUE (uuid)
);
```

**Sample Data:**
```sql
INSERT INTO public.collection (name, description, code) VALUES
    ('Electronics', 'All electronic items', 'COLL_ELEC'),
    ('Furniture', 'Various furniture items', 'COLL_FURN'),
    ('Books', 'Different genres of books', 'COLL_BOOK'),
    ('Clothing', 'Apparel and accessories', 'COLL_CLOTH');
```

#### 2. g5_product

```sql
CREATE TABLE public.g5_product (
    product_id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    product_name text NOT NULL,
    product_description text,
    product_stock_qty integer,
    currency character varying,
    product_price numeric(12,4),
    collection_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT g5_product_pkey PRIMARY KEY (product_id),
    CONSTRAINT g5_product_collection_fkey FOREIGN KEY (collection_id)
        REFERENCES public.collection (collection_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT g5_product_name_collection_unique UNIQUE (product_name, collection_id)
);
```

**Sample Products:** See `README-docker.md` lines 104-213 for full sample data (24 products across 4 collections).

---

## Integration with Llama 3.2

### Intent Classification

Added `catalog_inquiry` intent to `intent_classifier.py`:

```python
intent_categories = [
    "order_inquiry",
    "catalog_inquiry",      # NEW
    "general_chat",
    "tool_usage",
    ...
]
```

**Intent Description:**
> "Questions about available products, collections, catalog, product search, what's in stock"

**Suggested Tools:**
```python
"catalog_inquiry": ["listcollections", "getcatalog", "searchproducts"]
```

### Tool Detection Prompt

Updated `v2_llama_optimized.py` with catalog examples:

```
Examples:
- "What collections do you have?" 
  → {"tool_name": "listcollections", "parameters": {}, "confidence": 0.95}

- "Show me Electronics catalog" 
  → {"tool_name": "getcatalog", "parameters": {"collection_name": "Electronics"}, "confidence": 0.9}

- "Find laptops under 50000" 
  → {"tool_name": "searchproducts", "parameters": {"keyword": "laptop", "max_price": 50000}, "confidence": 0.9}
```

### Tool Registration

Tools auto-register via `BaseCCCPTool` subclass detection in `registry.py`:

```python
# Automatic discovery - no manual registration needed!
for tool in BaseCCCPTool.__subclasses__():
    if issubclass(tool, BaseCCCPTool):
        self.register_tool(tool)
```

**Registered Tool Names:**
- `listcollections`
- `getcatalog`
- `searchproducts`
- `placeorder` (stub)

### LLM Tool Selection Process

1. User inputs query: *"What products are in Electronics?"*
2. Llama 3.2 receives tools info:
   ```
   Tool: getcatalog
   Description: Get product catalog with optional filters...
   Parameters: collection_name: Optional[str], min_price: Optional[float], ...
   ```
3. LLM generates JSON:
   ```json
   {
     "tool_name": "getcatalog",
     "parameters": {"collection_name": "Electronics"},
     "confidence": 0.9,
     "reasoning": "User wants Electronics products"
   }
   ```
4. Agent executes tool with parameters
5. Tool queries database via MCP client
6. Response formatted and returned to user

---

## Testing Strategy

### Unit Tests (`tests/unit/test_catalog_tools.py`)

**Coverage:** 30+ test cases

**Test Categories:**

1. **Tool Initialization**
   - Tool name and description
   - Input/output schema

2. **Input Validation**
   - Required parameters
   - Optional parameters
   - Invalid inputs
   - Price range validation

3. **Database Operations** (Mocked)
   - Successful queries
   - Empty results
   - Database errors

4. **Utility Functions**
   - Filter clause building
   - Price formatting
   - Text/JSON formatting

**Running Unit Tests:**
```bash
# Activate virtual environment
cd /Users/achappa/devhak/gfc
source uv3135b/bin/activate

# Run unit tests
cd common
pytest tests/unit/test_catalog_tools.py -v
```

### Integration Tests (`tests/integration/test_catalog_integration.py`)

**Coverage:** 15+ test cases

**Prerequisites:**
- Docker Postgres running on `localhost:5432`
- Database populated with sample data from `README-docker.md`
- Environment variables set:
  ```bash
  export POSTGRES_HOST=localhost
  export POSTGRES_PORT=5432
  export POSTGRES_USER=postgres
  export POSTGRES_PASSWORD=postgres
  export POSTGRES_DB=postgres
  ```

**Test Categories:**

1. **Real Database Queries**
   - List all collections
   - Get full catalog
   - Filter by collection
   - Filter by price
   - Search by keyword

2. **Data Validation**
   - Expected collections exist
   - Expected products exist
   - Correct formatting

3. **Workflow Tests**
   - Complete user journey
   - Multi-step queries

**Running Integration Tests:**
```bash
# Ensure Docker Postgres is running
docker-compose up -d

# Run integration tests
pytest tests/integration/test_catalog_integration.py -v -s
```

---

## Usage Examples

### Example 1: List Collections

**User Query:** *"What collections do you have?"*

**LLM Detection:**
```json
{
  "tool_name": "listcollections",
  "parameters": {},
  "confidence": 0.95
}
```

**Tool Execution:**
```python
from cccp.tools.catalog.list_collections import ListCollectionsTool

tool = ListCollectionsTool()
result = tool.run()
print(result)
```

**Output:**
```
🛍️  **Available Collections:**

📦 **Electronics** (COLL_ELEC)
   └─ 6 products
📦 **Furniture** (COLL_FURN)
   └─ 6 products
📦 **Books** (COLL_BOOK)
   └─ 6 products
📦 **Clothing** (COLL_CLOTH)
   └─ 6 products

✨ Total: 4 collections with 24 products
```

### Example 2: Get Collection Catalog

**User Query:** *"Show me products in Electronics under 20000"*

**LLM Detection:**
```json
{
  "tool_name": "getcatalog",
  "parameters": {
    "collection_name": "Electronics",
    "max_price": 20000
  },
  "confidence": 0.9
}
```

**Tool Execution:**
```python
from cccp.tools.catalog.get_catalog import GetCatalogTool

tool = GetCatalogTool()
result = tool.run(collection_name="Electronics", max_price=20000.0)
print(result)
```

### Example 3: Search Products

**User Query:** *"Find Samsung phones"*

**LLM Detection:**
```json
{
  "tool_name": "searchproducts",
  "parameters": {
    "keyword": "Samsung"
  },
  "confidence": 0.9
}
```

**Tool Execution:**
```python
from cccp.tools.catalog.search_products import SearchProductsTool

tool = SearchProductsTool()
result = tool.run(keyword="Samsung")
print(result)
```

### Example 4: Complex Search

**User Query:** *"Show me chairs under 10000 in Furniture"*

**LLM Detection:**
```json
{
  "tool_name": "searchproducts",
  "parameters": {
    "keyword": "chair",
    "collection_name": "Furniture",
    "max_price": 10000
  },
  "confidence": 0.9
}
```

**Tool Execution:**
```python
tool = SearchProductsTool()
result = tool.run(
    keyword="chair",
    collection_name="Furniture",
    max_price=10000.0
)
print(result)
```

---

## Phase 2 Planning

### Place Order Tool Implementation

**Status:** Stub created, awaiting implementation approval

**Required Database Tables:**

1. **g5_customer** - User registration
2. **g5_order** - Order records
3. **g5_order_item** - Order line items  
4. **g5_payment** - Synthetic payment records

**Workflow:**

```
1. Validate User
   ├─ Check g5_customer exists
   └─ Get customer_id

2. Validate Products & Stock
   ├─ For each item:
   │  ├─ Check product exists
   │  ├─ Check stock >= quantity
   │  └─ Get price
   └─ Calculate order total

3. Begin Transaction
   │
   ├─ 4. Create Order Record
   │     └─ INSERT INTO g5_order
   │
   ├─ 5. Create Order Items
   │     └─ INSERT INTO g5_order_item (foreach)
   │
   ├─ 6. Process Payment
   │     ├─ Generate transaction_id
   │     └─ INSERT INTO g5_payment
   │
   ├─ 7. Update Inventory
   │     └─ UPDATE g5_product SET stock -= qty
   │
   └─ 8. Commit Transaction

9. Generate Confirmation
   └─ Return order_id, items, total, status
```

**Error Handling:**
- Rollback on any failure
- Handle race conditions (concurrent orders)
- Stock validation at transaction level

**Testing Requirements:**
- Unit tests for each step
- Integration tests with test DB
- Race condition testing
- Rollback verification

**Timeline:** Awaiting user approval to proceed with Phase 2

---

## Troubleshooting

### Issue: Tools not registered

**Symptoms:** LLM can't find catalog tools

**Solution:**
```python
from cccp.tools.registry import get_all_tools

tools = get_all_tools()
print([t.name for t in tools])
# Should include: listcollections, getcatalog, searchproducts
```

**If missing:** Ensure `catalog/__init__.py` imports are correct

### Issue: Database connection failed

**Symptoms:** `ToolError: Database error`

**Check:**
1. Docker Postgres running: `docker ps`
2. Environment variables set
3. MCP server accessible: `netstat -an | grep 5432`

**Logs:**
```python
# Enable DEBUG logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Issue: LLM not detecting catalog tools

**Check:**
1. Prompt version: `PromptConfig.get_active_version("tool_detection")`
   - Should be: `TOOL_DETECTION_V2_LLAMA_OPTIMIZED`

2. Tools info generated:
   ```python
   agent = CustomToolCallingAgent()
   tools_info = agent._get_tools_info()
   print(tools_info)  # Should include catalog tools
   ```

3. LLM temperature: Should be low (0.1-0.2) for consistent tool detection

### Issue: Empty results from database

**Check:**
1. Sample data loaded:
   ```sql
   SELECT COUNT(*) FROM collection;  -- Should be 4
   SELECT COUNT(*) FROM g5_product;  -- Should be 24
   ```

2. If empty, load sample data from `README-docker.md` lines 60-213

### Issue: Formatting looks wrong

**Check:**
- Client supports Unicode (for ₹, 📦 symbols)
- Use `format_catalog_json()` for programmatic access
- Use `format_catalog_text()` for display

---

## Appendix

### File Locations

**Core Implementation:**
```
src/cccp/tools/catalog/
src/cccp/tools/order/place_order.py
src/cccp/agents/intent_classifier.py
src/cccp/prompts/tool_detection/v2_llama_optimized.py
```

**Tests:**
```
tests/unit/test_catalog_tools.py
tests/integration/test_catalog_integration.py
```

**Documentation:**
```
z_additional_md/CATALOG_TOOLS_IMPLEMENTATION.md
README-docker.md (database schema and sample data)
```

### Key Dependencies

- `cccp.tools.base.BaseCCCPTool` - Base class for all tools
- `cccp.mcp.client.MCPPostgresClient` - Database connection
- `cccp.core.logging` - Logging infrastructure
- `cccp.core.exceptions.ToolError` - Error handling

### Environment Variables

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres

# MCP Server Configuration
MCP_POSTGRES_HOST=localhost
MCP_POSTGRES_PORT=8001
MCP_POSTGRES_ENABLED=true

# Model Configuration
MODEL_NAME=llama3.2:latest
MODEL_TYPE=auto
MODEL_TEMPERATURE=0.2
```

### Next Steps

1. ✅ Phase 1 Complete - Catalog tools implemented and tested
2. ⏸️ Awaiting user confirmation and approval
3. 🚧 Phase 2 - Implement PlaceOrderTool
   - Create database tables
   - Implement order workflow
   - Add synthetic payment processing
   - Test with user registration integration

---

## Conclusion

Phase 1 of the Product Catalog Tools implementation is **complete and production-ready**. The system provides:

✅ Three fully functional catalog tools  
✅ Natural language query support via Llama 3.2  
✅ Dynamic filtering and search capabilities  
✅ Human-friendly formatted responses  
✅ Comprehensive test coverage (unit + integration)  
✅ Extensive logging for debugging  
✅ Foundation for Phase 2 order placement  

The implementation follows best practices:
- Clean architecture with separation of concerns
- Reusable utility functions
- Comprehensive error handling
- Auto-discovery tool registration
- Async/sync compatibility
- Type hints and documentation

**Ready for deployment and testing with real users!**

---

*Document generated: October 10, 2025*  
*Last updated: October 10, 2025*  
*Version: 1.0*

