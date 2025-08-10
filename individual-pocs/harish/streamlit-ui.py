#test interface for conversational chatbot

import streamlit as st
import requests
import json

#configure FAST API server URL
FAPI_URL = "http://localhost:8000"


st.title("Geni5")
st.subheader("Conversational Chatbot Interface")
# Display a welcome message
st.write("Welcome to the Geni5 chatbot! You can chat with the bot below.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


with st.chat_message("assistant"):
# Input for user messages
    welcome_message = "Hello! How can I assist you today?"
    prompt = st.chat_input(welcome_message)
    st.session_state.messages.append({"role": "chatbot", "content": prompt})

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send the user message to the FastAPI server
    try:
        response = requests.post(
            f"{FAPI_URL}/chat",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"message": prompt, "user_id": "default_user"})
        )
    except Exception as e:
            st.error(f"Error: {str(e)}")

