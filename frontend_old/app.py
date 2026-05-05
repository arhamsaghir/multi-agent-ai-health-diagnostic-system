"""Streamlit dashboard — main entry point."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from frontend.pages.diagnosis import show_diagnosis_page
from frontend.pages.vision import show_vision_page
from frontend.pages.chat import show_chat_page
from frontend.pages.history import show_history_page
from frontend.pages.about import show_about_page

# Page config
st.set_page_config(
    page_title="AI Health Diagnostic System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom theme
st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #1a1a2e; }
    .severity-critical { color: #dc3545; font-weight: bold; }
    .severity-high { color: #fd7e14; font-weight: bold; }
    .severity-moderate { color: #ffc107; font-weight: bold; }
    .severity-low { color: #28a745; font-weight: bold; }
    .agent-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; background: #e9ecef; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🏥 AI Health Diagnostics")
    st.caption("Multi-Agent Diagnostic System")

    page = st.radio(
        "Navigate",
        ["Diagnosis", "Vision", "Chat", "History", "About"],
        label_visibility="collapsed",
    )

    st.divider()
    st.info("**Disclaimer:** This is a research project. Always consult a healthcare professional for medical advice.")

# Route to pages
if page == "Diagnosis":
    show_diagnosis_page()
elif page == "Vision":
    show_vision_page()
elif page == "Chat":
    show_chat_page()
elif page == "History":
    show_history_page()
elif page == "About":
    show_about_page()
