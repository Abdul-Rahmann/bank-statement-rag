"""
Utility Functions
Helper functions for the Streamlit app
"""

import json
import os
import streamlit as st
from src.rag_system import BankStatementRAG


def load_config():
    """Load configuration from file."""
    if os.path.exists('config.json'):
        with open('config.json') as f:
            return json.load(f)
    return None


def initialize_rag(force_refresh=False):
    """Initialize the RAG system."""
    config = load_config()
    if config is None:
        st.error("Config file not found. Please create config.json")
        return False

    try:
        with st.spinner("Initializing RAG system..."):
            st.session_state.rag = BankStatementRAG(config, force_refresh=force_refresh)
            if st.session_state.rag.transactions_df is not None and len(st.session_state.rag.transactions_df) > 0:
                st.session_state.transactions_df = st.session_state.rag.get_dataframe()
                return True
            else:
                st.error("No transaction data found. Please add PDFs to data/raw/ and refresh.")
                return False
    except Exception as e:
        st.error(f"Error initializing system: {e}")
        return False


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'rag' not in st.session_state:
        st.session_state.rag = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'transactions_df' not in st.session_state:
        st.session_state.transactions_df = None
