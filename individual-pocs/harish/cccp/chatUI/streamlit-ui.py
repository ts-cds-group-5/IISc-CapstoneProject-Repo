#test interface for conversational chatbot

import streamlit as st
import requests
import json


#configure FAST API server URL
FAPI_URL = "http://localhost:8000"

#readme: streamlit run /Users/achappa/devhak/cccp/chatUI/streamlit-ui.py

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

#sample implementation for FastAPI server
with st.chat_message("assistant"):
    # Input for user messages
    welcome_message = "Hello! How can I assist you today?"
    prompt = st.chat_input(welcome_message)
    #st.session_state.messages.append({"role": "chatbot", "content": prompt})

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        #https://fmelihh.medium.com/a-practical-guide-to-mcp-elicitation-with-fastapi-fastmcp-65f57fd91896
        # Send the user message to the FastAPI server and wait for a response with wait=True
        try:
            #print data to be sent
            print(f"Sending prompt to FastAPI server: {prompt}")
            #call generate endpoint
            response = requests.post(
                f"{FAPI_URL}/generate",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"prompt": prompt, "user_id": "default_user"})
            )
            response_data = response.json()
            print(f"Response data from FastAPI server: {response_data}")
            
            #parse the response data to get the generated text
            generated_text = response_data.get("generated_text", "")
            print(f"Received response from FastAPI server: {generated_text}")

            with st.chat_message("assistant"):
                #st.markdown(generated_text)
                #copy only the "Answer:" part and send to chat
                if "Output:" in generated_text:
                    answer_part = generated_text.split("Output:###Response:")[-1].strip()
                    print(f"inside answer part: {generated_text}")
                    print(f"Extracted answer part: {answer_part}")
                    st.markdown(answer_part)
                else:
                    answer_part = generated_text
                    st.markdown(generated_text)
                #append to session state messages
            
            st.session_state.messages.append({"role": "assistant", "content": answer_part})
            
            #handle exceptions and http errors
            if response.status_code != 200:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")