# CCCP Advanced Chat Flow - With Catalog Tools (Updated)

## Complete System Architecture

```mermaid
graph TD
    A[User Input] --> B{User Session Exists?}
    B -->|No| C[User Registration Detection]
    B -->|Yes| D[Tool Detection]
    
    C --> C1[Extract User Info]
    C1 --> C2[Store Session]
    C2 --> C3[Welcome Message]
    
    D --> D1{LLM Tool Detection}
    D1 -->|Success JSON| E{Intent Classification}
    D1 -->|Failed/Low Confidence| D2[Regex Fallback]
    
    D2 --> D3{Pattern Match?}
    D3 -->|Collection Query| CAT1[Catalog Tools]
    D3 -->|Order Query| ORD1[Order Tools]
    D3 -->|Math Operation| MATH1[Math Tools]
    D3 -->|No Match| G[LangGraph Agent]
    
    E -->|catalog_inquiry| CAT1
    E -->|order_inquiry| ORD1
    E -->|tool_usage| MATH1
    E -->|general_chat| G
    
    CAT1 --> CAT2{Which Catalog Tool?}
    CAT2 -->|Collections List| CAT3[ListCollectionsTool]
    CAT2 -->|Catalog Query| CAT4[GetCatalogTool]
    CAT2 -->|Product Search| CAT5[SearchProductsTool]
    
    CAT3 --> DB1[MCP Postgres Client]
    CAT4 --> DB1
    CAT5 --> DB1
    
    DB1 --> DB2[Query: collection + g5_product tables]
    DB2 --> CAT6[Format Response]
    CAT6 --> RESP[Tool Response]
    
    ORD1 --> ORD2{Extract Parameters}
    ORD2 -->|Specific cart_id| ORD3[GetOrderTool by ID]
    ORD2 -->|Session Email| ORD4[GetOrderTool by Email]
    ORD2 -->|Session Name| ORD5[GetOrderTool by Name]
    
    ORD3 --> DB3[MCP Postgres Client]
    ORD4 --> DB3
    ORD5 --> DB3
    DB3 --> DB4[Query: cart table]
    DB4 --> ORD6[Format with Context]
    ORD6 --> RESP
    
    MATH1 --> MATH2{Math Operation}
    MATH2 -->|Addition| MATH3[AddTool]
    MATH2 -->|Multiplication| MATH4[MultiplyTool]
    MATH3 --> RESP
    MATH4 --> RESP
    
    G --> G1[Chat Node]
    G1 --> G2[Model Service]
    G2 --> G3{Model Type?}
    G3 -->|Ollama| G4[Ollama + RAG]
    G3 -->|Phi-2| G5[Phi-2 Model]
    G4 --> G6[Generate Response]
    G5 --> G6
    
    C3 --> FINAL[ChatResponse]
    RESP --> FINAL
    G6 --> FINAL
    FINAL --> L[Return to User]
    
    style A fill:#e1f5fe
    style L fill:#c8e6c9
    style CAT1 fill:#fff59d,stroke:#f57f17,stroke-width:3px
    style CAT2 fill:#fff9c4
    style CAT3 fill:#fff9c4
    style CAT4 fill:#fff9c4
    style CAT5 fill:#fff9c4
    style ORD1 fill:#c5e1a5,stroke:#33691e,stroke-width:3px
    style ORD2 fill:#dcedc8
    style MATH1 fill:#ffccbc
    style DB1 fill:#b3e5fc,stroke:#0277bd,stroke-width:2px
    style DB2 fill:#b3e5fc
    style DB3 fill:#b3e5fc
    style DB4 fill:#b3e5fc
    style RESP fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```

## Updated Tool System

```mermaid
graph LR
    subgraph "Tool Registry (7 Tools)"
        T1[listcollections]
        T2[getcatalog]
        T3[searchproducts]
        T4[getorder]
        T5[placeorder - stub]
        T6[add]
        T7[multiply]
    end
    
    subgraph "Catalog Tools - NEW"
        T1
        T2
        T3
    end
    
    subgraph "Order Tools"
        T4
        T5
    end
    
    subgraph "Math Tools"
        T6
        T7
    end
    
    T1 --> DB[(PostgreSQL)]
    T2 --> DB
    T3 --> DB
    T4 --> DB
    
    style T1 fill:#fff59d
    style T2 fill:#fff59d
    style T3 fill:#fff59d
    style T4 fill:#c5e1a5
    style T5 fill:#d3d3d3,stroke-dasharray: 5 5
    style T6 fill:#ffccbc
    style T7 fill:#ffccbc
    style DB fill:#b3e5fc
```

## Intent Classification Flow

```mermaid
graph TD
    A[User Query] --> B[Intent Classifier]
    B --> C{Classify Intent}
    
    C -->|catalog_inquiry| I1[Catalog Intent]
    C -->|order_inquiry| I2[Order Intent]
    C -->|tool_usage| I3[Tool Usage Intent]
    C -->|general_chat| I4[General Chat Intent]
    
    I1 --> T1[Suggested Tools:<br/>listcollections<br/>getcatalog<br/>searchproducts]
    I2 --> T2[Suggested Tools:<br/>getorder]
    I3 --> T3[Suggested Tools:<br/>add, multiply, getorder]
    I4 --> T4[No Tools]
    
    T1 --> E[Tool Execution]
    T2 --> E
    T3 --> E
    T4 --> M[LLM Response]
    
    style I1 fill:#fff59d,stroke:#f57f17,stroke-width:2px
    style I2 fill:#c5e1a5
    style I3 fill:#ffccbc
    style I4 fill:#e0e0e0
```

## Catalog Tool Detection & Execution

```mermaid
graph TD
    A[User: 'Show me Books'] --> B[LLM Tool Detection]
    B -->|JSON Parse Success| C[Tool: getcatalog<br/>Params: collection='Books']
    B -->|JSON Parse Fail| D[Regex Fallback]
    
    D --> D1{Collection Detected?}
    D1 -->|books + show| C
    
    C --> E[GetCatalogTool.run]
    E --> F[Build SQL Query]
    F --> F1[Base Query + WHERE clauses]
    F1 --> F2[Positional Params: $1, $2, $3]
    
    F2 --> G[MCP Postgres Client]
    G --> H[Execute Query]
    H --> I[Format Results]
    
    I --> J{Results Found?}
    J -->|Yes| K[Format Catalog Text<br/>with emojis]
    J -->|No| L[Helpful 'Not Found' Message]
    
    K --> M[Return to User]
    L --> M
    
    style A fill:#e1f5fe
    style C fill:#fff59d
    style E fill:#fff59d
    style G fill:#b3e5fc
    style M fill:#c8e6c9
```

## Order Query with Session Fallback

```mermaid
graph TD
    A[User: 'I placed an order earlier'] --> B[Tool Detection]
    B --> C[getorder detected]
    
    C --> D[Extract Parameters]
    D --> E{Cart ID Pattern?}
    E -->|cart 454| F1[Use cart_id=454]
    E -->|No match| E2{Email in Query?}
    
    E2 -->|Yes| F2[Use extracted email]
    E2 -->|No| E3{Order Keywords?}
    
    E3 -->|order, earlier| E4{Session Email?}
    E4 -->|Yes| F3[Use session email]
    E4 -->|No| F4[Empty params - Error]
    
    F1 --> G[GetOrderTool.run]
    F2 --> G
    F3 --> G
    F4 --> G
    
    G --> H[MCP Query Cart Table]
    H --> I{Cart Found?}
    
    I -->|Yes| J[Format with Context<br/>'Searched by email: ...']
    I -->|No - by email| K[Helpful Message:<br/>'No cart for your email']
    I -->|No - by ID| L[Error: Cart not found]
    
    J --> M[Return to User]
    K --> M
    L --> M
    
    style A fill:#e1f5fe
    style C fill:#c5e1a5
    style F3 fill:#aed581,stroke:#33691e,stroke-width:2px
    style J fill:#c8e6c9
    style K fill:#fff9c4
    style M fill:#c8e6c9
```

## Database Schema

```mermaid
erDiagram
    COLLECTION ||--o{ G5_PRODUCT : contains
    CART ||--o{ CART_ITEM : has
    G5_PRODUCT ||--o{ CART_ITEM : referenced_in
    
    COLLECTION {
        int collection_id PK
        uuid uuid
        varchar name
        text description
        varchar code
        timestamp created_at
        timestamp updated_at
    }
    
    G5_PRODUCT {
        int product_id PK
        text product_name
        text product_description
        int product_stock_qty
        varchar currency
        numeric product_price
        int collection_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    CART {
        int cart_id PK
        varchar customer_email
        varchar customer_full_name
        varchar user_ip
        numeric grand_total
        text shipping_note
        varchar status
        timestamp created_at
        timestamp updated_at
    }
    
    CART_ITEM {
        int item_id PK
        int cart_id FK
        int product_id FK
        int quantity
        numeric unit_price
        numeric total_price
    }
```

## Supported User Queries

```mermaid
mindmap
  root((User Queries))
    Catalog Queries
      Collections
        What collections?
        Show collections
        List collections
      Specific Collection
        Show me Books
        Get Electronics
        All Furniture
        Books?
        Give me Clothing
      Price Filtering
        Under 10000
        Products below 5000
        Electronics under 20000
      Search
        Find laptops
        Search Samsung
        Looking for chairs
    Order Queries
      Specific Cart
        cart 454
        order 123
        my cart cart789
      Vague Queries
        I placed an order earlier
        my order
        order status
      Properties
        order with total 330
        shipment details
        delivery status
    Math Operations
      add 5 and 3
      multiply 10 by 20
```

## Parameter Extraction Logic

```mermaid
graph TD
    A[User Query] --> B{Tool Type}
    
    B -->|getorder| C[Order Parameter Extraction]
    B -->|getcatalog| D[Catalog Parameter Extraction]
    B -->|searchproducts| E[Search Parameter Extraction]
    
    C --> C1{Cart ID Pattern?}
    C1 -->|cart 454| C2[cart_id=454]
    C1 -->|No| C3{Email Pattern?}
    C3 -->|Yes| C4[customer_email=...]
    C3 -->|No| C5{Order Keywords?}
    C5 -->|Yes| C6[Use Session Email/Name]
    C5 -->|No| C7[Empty Params]
    
    D --> D1{Collection in Query?}
    D1 -->|Books| D2[collection_name=Books]
    D1 -->|No| D3{Price Pattern?}
    D3 -->|under 5000| D4[max_price=5000]
    D3 -->|No| D5[No Filters]
    
    E --> E1[Extract Keyword]
    E1 --> E2[keyword=...]
    E2 --> E3[+ Catalog Filters]
    
    C2 --> F[Execute Tool]
    C4 --> F
    C6 --> F
    D2 --> F
    D4 --> F
    D5 --> F
    E3 --> F
    
    style C6 fill:#aed581,stroke:#33691e,stroke-width:2px
    style D2 fill:#fff59d
    style E2 fill:#fff59d
    style F fill:#c8e6c9
```

## Tool Registry & Auto-Discovery

```mermaid
graph TD
    A[Application Startup] --> B[Import tools/__init__.py]
    B --> C[Import Catalog Tools]
    
    C --> C1[ListCollectionsTool]
    C --> C2[GetCatalogTool]
    C --> C3[SearchProductsTool]
    C --> C4[PlaceOrderTool stub]
    
    B --> D[Import Existing Tools]
    D --> D1[AddTool]
    D --> D2[MultiplyTool]
    D --> D3[GetOrderTool]
    
    C1 --> E[BaseCCCPTool Subclass]
    C2 --> E
    C3 --> E
    C4 --> E
    D1 --> E
    D2 --> E
    D3 --> E
    
    E --> F[Tool Registry]
    F --> G[Auto-Discovery via __subclasses__]
    G --> H[Register All Tools]
    
    H --> I[7 Tools Available]
    I --> J[LLM Tool Detection]
    
    style C1 fill:#fff59d
    style C2 fill:#fff59d
    style C3 fill:#fff59d
    style C4 fill:#d3d3d3,stroke-dasharray: 5 5
    style F fill:#b39ddb
    style I fill:#c8e6c9
```

## Llama 3.2 Tool Detection Flow

```mermaid
graph TD
    A[User Input] --> B[Get Available Tools Info]
    B --> C[Generate v2_llama_optimized Prompt]
    
    C --> D[Llama 3.2 LLM]
    D --> E{JSON Response?}
    
    E -->|Valid JSON| F{Tool Detected?}
    E -->|Empty/Invalid| G[Regex Fallback]
    
    F -->|tool_name + params| H[Execute Tool]
    F -->|null/low confidence| G
    
    G --> I{Pattern Match?}
    I -->|Collection keyword| J1[getcatalog]
    I -->|Collections list| J2[listcollections]
    I -->|Search keyword| J3[searchproducts]
    I -->|Order keyword| J4[getorder]
    I -->|Math pattern| J5[add/multiply]
    I -->|No match| K[General Chat]
    
    J1 --> H
    J2 --> H
    J3 --> H
    J4 --> H
    J5 --> H
    
    H --> L[Tool Result]
    K --> M[LLM Response]
    
    L --> N[Return to User]
    M --> N
    
    style D fill:#9fa8da,stroke:#3f51b5,stroke-width:2px
    style G fill:#ffab91,stroke:#e64a19,stroke-width:2px
    style H fill:#c8e6c9
```

## Database Query Flow (Positional Parameters)

```mermaid
graph TD
    A[GetCatalogTool] --> B[Build Filter WHERE Clauses]
    B --> C[filters dict]
    
    C --> D{collection_name?}
    D -->|Books| E1[WHERE c.name = $1<br/>params: '1'='Books']
    D -->|No| E2[Skip]
    
    C --> F{max_price?}
    F -->|5000| G1[WHERE p.product_price <= $2<br/>params: '2'=5000]
    F -->|No| G2[Skip]
    
    C --> H{keyword?}
    H -->|laptop| I1[WHERE p.product_name ILIKE $3<br/>params: '3'='%laptop%']
    H -->|No| I2[Skip]
    
    E1 --> J[Combine WHERE Clauses]
    G1 --> J
    I1 --> J
    
    J --> K[Final SQL with Positional Params]
    K --> L[MCP Client.query sql, params]
    
    L --> M[MCP Server]
    M --> N[asyncpg: *params.values]
    N --> O[PostgreSQL Execution]
    O --> P[Results]
    
    style E1 fill:#fff59d
    style G1 fill:#fff59d
    style I1 fill:#fff59d
    style K fill:#b3e5fc
    style M fill:#90caf9
    style P fill:#c8e6c9
```

## Response Formatting

```mermaid
graph TD
    A[Query Results] --> B{Tool Type?}
    
    B -->|ListCollections| C1[Format Collections List]
    B -->|GetCatalog| C2[Format Catalog]
    B -->|SearchProducts| C3[Format Search Results]
    B -->|GetOrder| C4[Format Order Details]
    
    C1 --> D1[🛍️ Available Collections:<br/>📦 Electronics 6 products<br/>📦 Furniture 6 products<br/>...]
    
    C2 --> D2[📋 Product Catalog<br/>📦 Books<br/>• Product Name<br/>  Price: ₹ 599.00<br/>  Stock: 120 available<br/>...]
    
    C3 --> D3[Found 2 products matching 'laptop'<br/>📋 Product Catalog<br/>• Lenovo IdeaPad...<br/>...]
    
    C4 --> D4{Search Method?}
    D4 -->|By Email| D41[Cart details for Harish<br/>Searched by email: ...<br/>Cart ID 454<br/>Total: ₹199.97]
    D4 -->|By Cart ID| D42[Cart details for Harish<br/>Cart ID 454<br/>Total: ₹199.97]
    
    D1 --> E[Return to User]
    D2 --> E
    D3 --> E
    D41 --> E
    D42 --> E
    
    style D1 fill:#fff9c4
    style D2 fill:#fff9c4
    style D3 fill:#fff9c4
    style D41 fill:#dcedc8
    style D42 fill:#dcedc8
    style E fill:#c8e6c9
```

## Complete System Overview

```mermaid
graph TD
    UI[User Interface<br/>Streamlit/API] --> AGENT[CustomToolCallingAgent]
    
    AGENT --> LLM[Llama 3.2<br/>v2_llama_optimized]
    LLM --> PARSE{Parse JSON}
    PARSE -->|Success| TOOLS
    PARSE -->|Fail| REGEX[Regex Fallback]
    REGEX --> TOOLS
    
    TOOLS[Tool Selection] --> CAT[Catalog Tools]
    TOOLS --> ORD[Order Tools]
    TOOLS --> MATH[Math Tools]
    
    CAT --> MCP1[MCP Client]
    ORD --> MCP1
    
    MCP1 --> PG[(PostgreSQL<br/>Docker)]
    
    PG --> TABLES[Tables:<br/>- collection<br/>- g5_product<br/>- cart]
    
    TABLES --> RES[Query Results]
    RES --> FMT[Format Response]
    FMT --> UI
    
    MATH --> CALC[Calculate]
    CALC --> FMT
    
    style UI fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    style AGENT fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style LLM fill:#9fa8da,stroke:#3f51b5,stroke-width:2px
    style CAT fill:#fff59d,stroke:#f57f17,stroke-width:2px
    style ORD fill:#c5e1a5,stroke:#33691e,stroke-width:2px
    style MATH fill:#ffccbc,stroke:#d84315,stroke-width:2px
    style PG fill:#b3e5fc,stroke:#0277bd,stroke-width:3px
    style FMT fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```

