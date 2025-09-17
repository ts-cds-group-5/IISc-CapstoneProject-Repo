### Project tasks
- [ ] Setting up the final project structure - @Chirag

### Set up Chat server for Human-Bot-Human agent journey
- [ ] Task 8: [ ] Saving chats in Postgres + connect to CSR part of streamlit - @prashanth & @Suchitra
 - [ ] Setup  chat db; needs some research on what chat to use (fast?)
 - [ ] Human agent streamlit app
 - [ ] App to send chat to human registered agent, with summary?

### Add tools to graph w/ MCP
- [ ] Task 7: Add tool to get data
    - [ ] Task 6.1: Ecomm commerce - simulation (db, app) -> evershop finalized, we will use this via docker app
    - [ ] Host MCP server locally for DB (pgsql)
    - [ ] Create MCP client node to fetch data

### Sentiment analysis tool
- [ ] Task 6: Add a tool to find sentiment given text (use model / using Goal-conditioned-value) @Harish, stretch goal
 - [ ] Task 6.1: Create strategy agent - or Strategy node? - defer?/ Understand->Decide. 

### Integrate basis sentiment analysis prompt node
- [ ]Task 4: Add a tool to find sentiment given text (use LLM prompt)
 - [ ] Async node to pass text to LLM and spit out sentiment in logger

### Integrate with Langgraph
- [ ] Task 3: Langgraph, with node for chatbot/LLM @harish
 - [ ] Task 3.2: ChatGPT setup @chirag
 - [ ] Task 3.1: Simple node 

### Basic app
- [x] Task 2: MSPB setup, use a simple model and chat template @Harish
 - [ ] Task 2.2: Ollama to work with prompt Template @chirag
 - [x] Task 2.1: [x] OLLama Setup, in local (Merge may be needed, Harish<>Chirag)
- [x] Task 1: Set up streamlit and fastapi @harish

### Adhoc tasks
- [ ] Merge Chirag’s code with Harish’s code
- [x] Add logger @Harish
- [x] Getting Debug to work in server_api
- [ ] Target for 13th sep -> getting Harish code merged with Chirag and getting Ollama and mspb with templating

### Garnishing stretch goals
 - [ ] Add memory across threads to detect prior conversation
 - [ ] Voice-text?

