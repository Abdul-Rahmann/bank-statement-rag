"""
Utility Functions
Helper functions for the Streamlit app
"""

import sys
import streamlit as st
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent.resolve()
sys.path.append(str(root_dir))

from src.rag_system import BankStatementRAG
from src.config import get_config


def initialize_rag(force_refresh=False):
    """Initialize the RAG system."""
    config = get_config()
    if config is None:
        st.error("Config file not found. Please create config.yml in the root directory of the project.")
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
