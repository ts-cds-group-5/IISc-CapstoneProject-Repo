"""Streamlit UI for CCCP Advanced."""

import streamlit as st
import requests
import json
from typing import Dict, Any, Optional
from cccp.core.logging import get_logger, setup_logging
from cccp.core.config import get_settings

# Setup logging
logger = get_logger(__name__)
setup_logging()

# Get settings
settings = get_settings()


class StreamlitApp:
    """Streamlit application for CCCP Advanced."""
    
    def __init__(self, api_url: str = None):
        self.api_url = api_url or f"http://{settings.api_host}:{settings.api_port}"
        self.logger = get_logger(f"{__name__}.StreamlitApp")
    
    def create_app(self) -> None:
        """Create and configure the Streamlit app."""
        st.set_page_config(
            page_title="CCCP Advanced",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Title and header
        st.title("🤖 Evershop Customer Support Chatbot")
        st.subheader("Evershop Customer Support Chatbot - Chat with our AI agent")
        
        # Sidebar
        self._create_sidebar()
        
        # Main chat interface
        self._create_chat_interface()
    
    def _create_sidebar(self) -> None:
        """Create the sidebar."""
        with st.sidebar:
            st.header("⚙️ Settings")
            
            # API Configuration
            st.subheader("API Configuration")
            api_url = st.text_input(
                "API URL",
                value=self.api_url,
                help="URL of the FastAPI server"
            )
            self.api_url = api_url
            
            # Model Settings
            st.subheader("Model Settings")
            max_length = st.slider(
                "Max Length",
                min_value=50,
                max_value=512,
                value=256,
                help="Maximum response length"
            )
            
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.2,
                step=0.1,
                help="Sampling temperature"
            )
            
            use_tools = st.checkbox(
                "Use Tools",
                value=True,
                help="Enable tool usage for math operations"
            )
            
            # Store settings in session state
            st.session_state.model_settings = {
                "max_length": max_length,
                "temperature": temperature,
                "use_tools": use_tools
            }
            
            # Status
            st.subheader("Status")
            if self._check_api_status():
                st.success("✅ API Connected")
            else:
                st.error("❌ API Disconnected")
    
    def _create_chat_interface(self) -> None:
        """Create the main chat interface."""
        # Welcome message
        st.write("Welcome to the Evershop customer support chatbot! You can chat with the bot below.")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self._get_chat_response(prompt)
                    if response:
                        # Format response for better display with newlines
                        formatted_response = response["response"].replace('\n', '\n\n')
                        st.markdown(formatted_response)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response["response"]
                        })
                    else:
                        st.error("Failed to get response from the server")
    
    def _get_chat_response(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get response from the chat API."""
        try:
            self.logger.info(f"Sending prompt to API: {prompt}")
            
            # Prepare request data
            request_data = {
                "prompt": prompt,
                "user_id": "streamlit_user",
                **st.session_state.get("model_settings", {})
            }
            
            # Make API request
            response = requests.post(
                f"{self.api_url}/api/v1/chat/generate",
                headers={"Content-Type": "application/json"},
                data=json.dumps(request_data),
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                self.logger.info(f"Received response: {response_data}")
                return response_data
            else:
                self.logger.error(f"API Error: {response.status_code} - {response.text}")
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            self.logger.error("Connection error: Could not connect to API")
            st.error("❌ Could not connect to the API server. Please check if the server is running.")
            return None
        except requests.exceptions.Timeout:
            self.logger.error("Timeout error: API request timed out")
            st.error("⏱️ Request timed out. Please try again.")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            st.error(f"❌ An error occurred: {str(e)}")
            return None
    
    def _check_api_status(self) -> bool:
        """Check if the API is accessible."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


def create_streamlit_app() -> None:
    """Create the Streamlit application."""
    app = StreamlitApp()
    app.create_app()


if __name__ == "__main__":
    create_streamlit_app()

