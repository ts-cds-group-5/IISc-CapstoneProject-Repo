<!-- ebdb8074-77a5-4b32-9807-2ad1292422d2 143f3d3e-591f-4c66-a883-f7dc2b43047c -->
# Streamlit Registration Form Implementation

## Overview

Transform the user registration from a conversational flow to a simple form with three fields (Name, Mobile Number, Email ID) that stays visible at the top of the chat interface. Users register via a Submit button before chatting, and User ID is auto-generated as a random 4-6 digit number.

## Files to Modify

### 1. Streamlit UI (`src/cccp/ui/streamlit_app.py`)

**Changes needed:**

- Add a registration form section at the top with:
  - Text input for Name
  - Text input for Mobile Number  
  - Text input for Email ID
  - Submit/Register button
- Generate random 4-6 digit User ID on registration
- Store registration data in `st.session_state`
- Disable chat input until user registers
- Pass user info (user_id, name, mobile, email) with each chat request
- Show registered user info in a compact banner after registration

**Key implementation details:**

```python
# Generate random User ID
import random
user_id = str(random.randint(1000, 999999))

# Store in session state
st.session_state.user_info = {
    'user_id': user_id,
    'name': name,
    'mobile': mobile,
    'email': email,
    'registered': True
}

# Pass to API in _get_chat_response()
request_data = {
    "prompt": prompt,
    "user_id": st.session_state.user_info['user_id'],
    "user_name": st.session_state.user_info['name'],
    "user_mobile": st.session_state.user_info['mobile'],
    "user_email": st.session_state.user_info['email'],
    ...
}
```

### 2. API Request Model (`src/cccp/api/models/requests.py`)

**Changes needed:**

- Add optional fields to `ChatRequest`:
  - `user_name: Optional[str]`
  - `user_mobile: Optional[str]`
  - `user_email: Optional[str]`
- These will be passed from UI to backend agent for user session initialization

### 3. Backend Agent (`src/cccp/agents/custom_tool_calling_agent.py`)

**Changes needed:**

- Modify `process_user_input()` to accept pre-registered user info from API
- Update `_detect_user_registration()` to check if user info is pre-provided
- Update `_handle_user_registration()` to include email field
- Modify `_request_user_registration()` message since it won't be shown (UI handles registration)
- Update `user_session` structure to include email:
  ```python
  self.user_session = {
      'user_id': user_id,
      'name': name,
      'mobile': mobile,
      'email': email,
      'registered_at': timestamp
  }
  ```


### 4. Chat Route (`src/cccp/api/routes/chat.py`)

**Changes needed:**

- Extract user info from `ChatRequest` (user_name, user_mobile, user_email)
- Pass user info to agent when invoking:
  ```python
  result = agent.invoke({
      "user_input": request.prompt,
      "user_info": {
          "user_id": request.user_id,
          "name": request.user_name,
          "mobile": request.user_mobile,
          "email": request.user_email
      }
  })
  ```


## Implementation Flow

1. User opens Streamlit UI and sees registration form at top
2. User fills Name, Mobile Number, Email ID and clicks Submit
3. UI generates random 4-6 digit User ID
4. Registration data stored in session state
5. Chat interface becomes enabled
6. Registered user info shown in compact banner
7. Each chat message includes user info in API request
8. Backend agent initializes user session with provided info
9. No conversational registration needed - agent can directly help with orders

## Benefits

- Cleaner UX with explicit registration step
- Users can update their info anytime (fields remain visible)
- Auto-generated User ID removes user burden
- Email field added for future use in conversations
- Backend receives complete user context from first message

### To-dos

- [x] Add registration form (Name, Mobile, Email) with Submit button and random User ID generation in streamlit_app.py
- [x] Add user_name, user_mobile, user_email optional fields to ChatRequest in requests.py
- [x] Extract and pass user info from ChatRequest to agent in chat.py
- [x] Modify agent to accept pre-registered user info and update user_session to include email in custom_tool_calling_agent.py

