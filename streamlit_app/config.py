"""
Configuration and Styling
Contains all Streamlit configuration and custom CSS
"""

import streamlit as st

def setup_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Bank Statement RAG Bot",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def load_custom_css():
    """Load custom CSS styling."""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
