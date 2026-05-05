"""Chat page — conversational symptom checking."""

import streamlit as st
import requests
from datetime import datetime


API_BASE = "http://localhost:8000"


def show_chat_page():
    """Render the conversational symptom checking page."""
    st.markdown('<p class="main-header">AI Health Chat</p>', unsafe_allow_html=True)
    st.caption("Have a conversation about your symptoms — ask questions and get guidance.")

    # Initialize session state
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar controls
    with st.sidebar:
        if st.button("New Conversation"):
            st.session_state.conversation_id = None
            st.session_state.chat_history = []
            st.rerun()

        st.divider()
        st.info("💡 Try asking:\n- 'I have a headache, what could it be?'\n- 'Is fever dangerous?'\n- 'When should I see a doctor?'")

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.markdown(f"**You:** {content}")
            else:
                st.markdown(f"**AI:** {content}")
            st.divider()

    # Safety alert display
    if st.session_state.get("last_safety_alert"):
        st.error(st.session_state.last_safety_message)
        st.session_state.last_safety_alert = False

    # Chat input
    user_input = st.chat_input("Describe your symptoms or ask a health question...")

    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
        })

        # Call API
        with st.spinner("AI is analyzing your symptoms..."):
            try:
                response = requests.post(
                    f"{API_BASE}/api/chat/message",
                    json={
                        "message": user_input,
                        "conversation_id": st.session_state.conversation_id,
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.conversation_id = data.get("conversation_id")

                    # Add AI response to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": data.get("response", "No response"),
                        "timestamp": datetime.now().isoformat(),
                    })

                    # Handle safety alerts
                    if data.get("safety_alert"):
                        st.session_state.last_safety_alert = True
                        st.session_state.last_safety_message = data.get("safety_message", "")
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Error: API returned status {response.status_code}",
                        "timestamp": datetime.now().isoformat(),
                    })
            except requests.ConnectionError:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "⚠️ API server is not running. Start it with `make api` to use the chat feature.",
                    "timestamp": datetime.now().isoformat(),
                })
            except Exception as e:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                })

        # Rerun to update display
        st.rerun()
