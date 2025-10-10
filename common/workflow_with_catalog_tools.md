# CCCP Advanced Chat Flow - Complete Shopping System (Updated Oct 2025)

## Complete System Architecture (Updated: Multi-Turn + Shopping Cart)

```mermaid
graph TD
    A[User Input] --> B{User Session Exists?}
    B -->|No| C[User Registration Detection]
    B -->|Yes| HIST[Load Conversation History<br/>Last 5 Turns]
    
    C --> C1[Extract User Info]
    C1 --> C2[Store Session + Init History]
    C2 --> C3[Welcome Message]
    
    HIST --> D[Tool Detection with Context]
    
    D --> D1{LLM Tool Detection<br/>Llama 3.2 + Context}
    D1 -->|Success + Confidence ≥ 0.7| E[Validated Tool Detection]
    D1 -->|Failed/Low Confidence| D2[Parse LLM Params]
    
    D2 --> D3[Regex Fallback + LLM Params]
    D3 --> D4{Pattern Match?}
    D4 -->|Order Query PRIORITY| ORD1[Order Tools]
    D4 -->|Address Pattern| CART5[Checkout Inferred]
    D4 -->|Collection Query| CAT1[Catalog Tools]
    D4 -->|Cart Operation| CART1[Cart Tools]
    D4 -->|Math Operation| MATH1[Math Tools]
    D4 -->|No Match| G[LangGraph Agent]
    
    E --> E1{Validate Params}
    E1 -->|Valid| EXEC[Execute Tool]
    E1 -->|Placeholders| D3
    
    CAT1 --> CAT2{Which Catalog Tool?}
    CAT2 -->|Collections List| CAT3[ListCollectionsTool]
    CAT2 -->|Catalog Query| CAT4[GetCatalogTool]
    CAT2 -->|Product Search| CAT5[SearchProductsTool]
    
    CAT3 --> DB1[MCP Postgres Client]
    CAT4 --> DB1
    CAT5 --> DB1
    
    DB1 --> DB2[Query: collection + g5_product]
    DB2 --> CAT6[Format Catalog Response]
    CAT6 --> RESP[Tool Response]
    
    CART1 --> CART2{Which Cart Tool?}
    CART2 -->|Add to Cart| CART3[AddToCartTool]
    CART2 -->|Remove| CART4[RemoveFromCartTool]
    CART2 -->|View| CART6[ViewCartTool]
    CART2 -->|Clear| CART7[ClearCartTool]
    CART2 -->|Checkout| CART5
    
    CART3 --> SESS1[Update Session Cart]
    CART4 --> SESS1
    CART6 --> SESS2[Read Session Cart]
    CART7 --> SESS1
    
    SESS1 --> RESP
    SESS2 --> RESP
    
    CART5 --> DB3[Create Order in g5_order]
    DB3 --> DB4[Create Items in g5_order_items]
    DB4 --> SESS3[Clear Session Cart]
    SESS3 --> RESP
    
    ORD1 --> ORD2{Extract/Inject Params}
    ORD2 -->|Specific cart_id| ORD3[Query by ID]
    ORD2 -->|Email in query| ORD4[Query by Email]
    ORD2 -->|Empty params| ORD5[Inject Session Email]
    
    ORD3 --> DB5[Dual-Table Query]
    ORD4 --> DB5
    ORD5 --> DB5
    
    DB5 --> DB6[1. Try g5_order + items]
    DB6 --> DB7{Found?}
    DB7 -->|Yes| ORD7[Format Order with Items]
    DB7 -->|No| DB8[2. Try cart table]
    DB8 --> DB9{Found?}
    DB9 -->|Yes| ORD8[Format Cart]
    DB9 -->|No| ORD9[Not Found Message]
    
    ORD7 --> RESP
    ORD8 --> RESP
    ORD9 --> RESP
    
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
    
    RESP --> TRACK[Save to Conversation History]
    G6 --> TRACK
    C3 --> TRACK
    
    TRACK --> FINAL[ChatResponse]
    FINAL --> L[Return to User]
    
    style A fill:#e1f5fe
    style HIST fill:#b39ddb,stroke:#4a148c,stroke-width:2px
    style L fill:#c8e6c9
    style CAT1 fill:#fff59d,stroke:#f57f17,stroke-width:3px
    style CART1 fill:#ffccbc,stroke:#d84315,stroke-width:3px
    style CART5 fill:#ef9a9a,stroke:#c62828,stroke-width:3px
    style ORD1 fill:#c5e1a5,stroke:#33691e,stroke-width:3px
    style ORD5 fill:#aed581,stroke:#33691e,stroke-width:2px
    style MATH1 fill:#ffccbc
    style DB5 fill:#90caf9,stroke:#0277bd,stroke-width:3px
    style DB6 fill:#b3e5fc
    style SESS1 fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px
    style TRACK fill:#b39ddb,stroke:#4a148c,stroke-width:2px
    style RESP fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```

## Complete Tool System (11 Production Tools)

```mermaid
graph LR
    subgraph "Tool Registry - 11 Tools"
        T1[listcollections]
        T2[getcatalog]
        T3[searchproducts]
        T4[addtocart]
        T5[removefromcart]
        T6[viewcart]
        T7[clearcart]
        T8[checkout]
        T9[getorder]
        T10[add]
        T11[multiply]
    end
    
    subgraph "Catalog Tools - 3"
        T1
        T2
        T3
    end
    
    subgraph "Shopping Cart Tools - 5"
        T4
        T5
        T6
        T7
        T8
    end
    
    subgraph "Order Tools - 1"
        T9
    end
    
    subgraph "Math Tools - 2"
        T10
        T11
    end
    
    T1 --> DB[(PostgreSQL)]
    T2 --> DB
    T3 --> DB
    T4 --> SESS[User Session<br/>Cart State]
    T5 --> SESS
    T6 --> SESS
    T7 --> SESS
    T8 --> DB2[(g5_order<br/>g5_order_items)]
    T9 --> DB3[(Dual Query:<br/>g5_order + cart)]
    
    SESS --> DB
    
    style T1 fill:#fff59d
    style T2 fill:#fff59d
    style T3 fill:#fff59d
    style T4 fill:#ffccbc
    style T5 fill:#ffccbc
    style T6 fill:#ffccbc
    style T7 fill:#ffccbc
    style T8 fill:#ef9a9a,stroke:#c62828,stroke-width:2px
    style T9 fill:#c5e1a5
    style T10 fill:#e0e0e0
    style T11 fill:#e0e0e0
    style DB fill:#b3e5fc
    style DB2 fill:#90caf9,stroke:#0277bd,stroke-width:2px
    style DB3 fill:#90caf9,stroke:#0277bd,stroke-width:2px
    style SESS fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px
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

## Order Query with Multi-Turn Context + Dual-Table Query (UPDATED)

```mermaid
graph TD
    A[User: 'show me my order'] --> B[Load Conversation History]
    B --> C[Tool Detection + Context]
    
    C --> D{LLM Detection}
    D -->|Success| E[getorder + params]
    D -->|Low Confidence| F[Regex Fallback]
    
    E --> G{Validate Params}
    G -->|Placeholder 'your_order_id'| F
    G -->|Valid| H
    
    F --> F1{Order Keywords?}
    F1 -->|Yes| F2{LLM Params Valid?}
    F2 -->|Yes| H[Extract Parameters]
    F2 -->|No| H
    
    H --> I{Cart ID Pattern?}
    I -->|cart 454, order 123| J1[Use cart_id]
    I -->|No match| I2{Email in Query?}
    
    I2 -->|Yes| J2[Use extracted email]
    I2 -->|No| I3{Order Keywords + Session?}
    
    I3 -->|Yes + Email exists| J3[Inject Session Email]
    I3 -->|Yes + Name exists| J4[Inject Session Name]
    I3 -->|No session| J5[Empty - Will inject later]
    
    J1 --> K{Empty Params Check}
    J2 --> K
    J3 --> K
    J4 --> K
    J5 --> K
    
    K -->|Empty params| K1[Agent Injects Session Email]
    K -->|Has params| L
    K1 --> L
    
    L[GetOrderTool.run] --> M[Dual-Table Query]
    
    M --> M1[1. Query g5_order table]
    M1 --> M2{Found in g5_order?}
    M2 -->|Yes| M3[Fetch g5_order_items]
    M3 --> N1[Format Order + Items<br/>Source: shopping cart]
    
    M2 -->|No| M4[2. Query cart table evershop]
    M4 --> M5{Found in cart?}
    M5 -->|Yes| N2[Format Cart<br/>Source: evershop]
    M5 -->|No| N3[Not Found Message]
    
    N1 --> O{Search Context?}
    N2 --> O
    N3 --> O
    
    O -->|By Email| P1[Add: 'Searched by your email']
    O -->|By ID| P2[Show: Cart/Order ID]
    O -->|Not found| P3[Helpful: 'No orders for email']
    
    P1 --> Q[Save to Conversation History]
    P2 --> Q
    P3 --> Q
    
    Q --> R[Return to User]
    
    style A fill:#e1f5fe
    style B fill:#b39ddb,stroke:#4a148c,stroke-width:2px
    style G fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style J3 fill:#aed581,stroke:#33691e,stroke-width:2px
    style K1 fill:#aed581,stroke:#33691e,stroke-width:2px
    style M1 fill:#90caf9,stroke:#0277bd,stroke-width:2px
    style M4 fill:#b3e5fc
    style N1 fill:#c8e6c9
    style N2 fill:#dcedc8
    style Q fill:#b39ddb,stroke:#4a148c,stroke-width:2px
    style R fill:#c8e6c9
```

## Database Schema (Updated with Shopping Cart Tables)

```mermaid
erDiagram
    COLLECTION ||--o{ G5_PRODUCT : contains
    G5_PRODUCT ||--o{ G5_ORDER_ITEMS : ordered_in
    G5_ORDER ||--o{ G5_ORDER_ITEMS : has
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
    
    G5_ORDER {
        int order_id PK
        varchar customer_name
        varchar customer_email
        varchar customer_phone
        text shipping_address
        text shipping_notes
        varchar currency
        varchar payment_mode
        varchar order_status
        numeric total_price
        timestamp created_at
        timestamp updated_at
    }
    
    G5_ORDER_ITEMS {
        int order_item_id PK
        int order_id FK
        int product_id FK
        text product_name
        varchar currency
        numeric unit_price
        int quantity
        numeric line_total
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

## Supported User Queries (Complete Shopping System)

```mermaid
mindmap
  root((User Queries))
    Catalog Queries
      Collections
        What collections?
        Show collections
        List collections
        what do you have?
      Specific Collection
        Show me Books
        Do you have Electronics?
        All Furniture
        Books?
        Give me Clothing
        show Electronics
      Price Filtering
        Under 10000
        Products below 5000
        Electronics under 20000
      Search
        Find laptops
        Search Samsung
        Looking for chairs
        Find Atomic Habits
    Shopping Cart
      Add to Cart
        Add Atomic Habits
        Add 2 Samsung Galaxy
        buy The White Tiger
        I want Lenovo laptop
      View Cart
        Show my cart
        View cart
        What's in my cart
      Remove from Cart
        Remove Atomic Habits
        Delete Samsung
        Take out The White Tiger
      Clear Cart
        Clear my cart
        Empty cart
        Reset cart
      Checkout
        Checkout
        Place order
        123 Main St Bangalore
        Ship to address...
    Order Queries
      Specific Order
        cart 454
        order 123
        my cart cart789
      Vague Queries NEW
        Do you have my order?
        show me my order
        my order status
        I placed an order earlier
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

## Llama 3.2 Tool Detection Flow (Enhanced: Context + Validation + Negative Examples)

```mermaid
graph TD
    A[User Input] --> A1[Load Conversation History]
    A1 --> A2[Format Last 5 Turns]
    A2 --> B[Get Available Tools Info]
    B --> C[Generate v2_llama_optimized Prompt<br/>28+ Examples + 5 Negative Samples]
    
    C --> C1[Include Conversation Context]
    C1 --> D[Llama 3.2 LLM]
    D --> E{JSON Response?}
    
    E -->|Valid JSON| F[Parse JSON]
    E -->|Empty/Invalid| G0[Extract Any LLM Params]
    
    F --> F1{Handle Flat/Nested JSON}
    F1 -->|Nested 'parameters' key| F2[Extract from params]
    F1 -->|Flat format| F3[Extract non-metadata keys]
    
    F2 --> F4{Tool + Confidence?}
    F3 --> F4
    
    F4 -->|tool_name + conf ≥ 0.7| H[Execute Tool]
    F4 -->|No tool/low confidence| G0
    
    G0 --> G[Regex Fallback + LLM Params]
    
    G --> I{Pattern Priority}
    I -->|1. Order keywords| J4[getorder]
    I -->|2. Address pattern| J6[checkout inferred]
    I -->|3. Cart keywords| J7[cart tools]
    I -->|4. Collection name| J1[getcatalog]
    I -->|5. Search keyword| J3[searchproducts]
    I -->|6. Collections list| J2[listcollections]
    I -->|7. Math pattern| J5[add/multiply]
    I -->|No match| K[General Chat]
    
    J4 --> V1{Validate LLM Params}
    V1 -->|Placeholder 'your_order_id'| V2[Discard, extract from input]
    V1 -->|Valid params| V3[Use LLM params]
    V2 --> H
    V3 --> H
    
    J1 --> V4{LLM Params Available?}
    V4 -->|Yes + valid| V5[Use LLM params]
    V4 -->|No| V6[Extract from regex]
    V5 --> H
    V6 --> H
    
    J2 --> H
    J3 --> H
    J5 --> H
    J6 --> H
    J7 --> H
    
    H --> H1{Empty Params for getorder?}
    H1 -->|Yes| H2[Inject Session Email]
    H1 -->|No| H3[Use Params]
    H2 --> L
    H3 --> L
    
    L[Tool Result] --> SAVE[Save to Conversation History<br/>Track: user input + tool used]
    K --> M[LLM Response]
    M --> SAVE
    
    SAVE --> N[Return to User]
    
    style A1 fill:#b39ddb,stroke:#4a148c,stroke-width:2px
    style C fill:#9fa8da,stroke:#3f51b5,stroke-width:2px
    style D fill:#9fa8da,stroke:#3f51b5,stroke-width:2px
    style F1 fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style G fill:#ffab91,stroke:#e64a19,stroke-width:2px
    style V1 fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style H2 fill:#aed581,stroke:#33691e,stroke-width:2px
    style SAVE fill:#b39ddb,stroke:#4a148c,stroke-width:2px
    style L fill:#c8e6c9
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

## Multi-Turn Shopping Flow Example (NEW - Oct 2025)

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent + Llama 3.2
    participant S as Session (Cart + History)
    participant DB as PostgreSQL
    
    Note over U,DB: Turn 1: Browse Catalog
    U->>A: "show me Books"
    A->>A: LLM detects: getcatalog(collection_name="Books")
    A->>DB: Query g5_product WHERE collection='Books'
    DB-->>A: 6 books found
    A->>S: Save turn: getcatalog
    A-->>U: 📋 Books Catalog (6 products)
    
    Note over U,DB: Turn 2: Add to Cart
    U->>A: "Add Atomic Habits"
    A->>S: Load history (Turn 1: getcatalog Books)
    A->>A: Context: User browsing Books
    A->>A: LLM detects: addtocart("Atomic Habits", qty=1)
    A->>DB: Find product "Atomic Habits"
    DB-->>A: Product found
    A->>S: Add to cart (1 item)
    A->>S: Save turn: addtocart
    A-->>U: ✅ Added Atomic Habits (₹699)
    
    Note over U,DB: Turn 3: Continue Browsing
    U->>A: "What about Electronics?"
    A->>S: Load history (Turn 1: getcatalog, Turn 2: addtocart)
    A->>A: Context: User shopping, cart has 1 item
    A->>A: LLM detects: getcatalog("Electronics")
    A->>DB: Query Electronics collection
    DB-->>A: 6 electronics found
    A->>S: Save turn: getcatalog
    A-->>U: 📋 Electronics Catalog (6 products)
    
    Note over U,DB: Turn 4: Add More Items
    U->>A: "Add 2 Samsung Galaxy"
    A->>S: Load history (3 turns, cart exists)
    A->>A: LLM detects: addtocart("Samsung Galaxy", qty=2)
    A->>DB: Find product
    DB-->>A: Samsung found
    A->>S: Update cart (2 items, 3 units)
    A->>S: Save turn: addtocart
    A-->>U: ✅ Added Samsung × 2 (₹33,998)
    
    Note over U,DB: Turn 5: Checkout (Address Only!)
    U->>A: "123 Main St, Bangalore 560001"
    A->>S: Load history (Turns with addtocart)
    A->>A: Context: User added items recently
    A->>A: Detects: Address pattern + cart context
    A->>A: Infers: checkout!
    A->>S: Validate cart (2 items)
    A->>DB: Create order in g5_order
    A->>DB: Create items in g5_order_items
    DB-->>A: Order #1 created
    A->>S: Clear cart
    A->>S: Save turn: checkout
    A-->>U: 📦 Order Confirmation #1
    
    Note over U,DB: Turn 6: Track Order (Vague Query!)
    U->>A: "show me my order"
    A->>S: Load history (Turn 5: checkout)
    A->>A: Context: User just checked out
    A->>A: LLM detects: getorder(params={})
    A->>A: Empty params → Inject session email
    A->>DB: Query g5_order by email (Dual-table)
    DB-->>A: Order #1 found (with items)
    A->>S: Save turn: getorder
    A-->>U: 📦 Order #1 Details (2 items)
    
    rect rgb(200, 230, 201)
        Note over U,DB: ✅ Complete Multi-Turn Flow<br/>6 Turns, 5 Tools Used<br/>Natural Conversation!
    end
```

