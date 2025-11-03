"""
Settings Page
System configuration and data management
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.resolve()
sys.path.append(str(root_dir))

import streamlit as st
from streamlit_app.utils import initialize_rag
from src.config import get_config


def render():
    """Render the settings page."""
    st.markdown('<p class="main-header">Settings</p>', unsafe_allow_html=True)

    st.subheader("System Configuration")

    config = get_config()
    if config:
        st.json(config)

    st.markdown("---")

    st.subheader("Data Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Refresh Data", type="primary"):
            if initialize_rag(force_refresh=True):
                st.success("Data refreshed successfully!")
                st.rerun()

    with col2:
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")

    st.markdown("---")

    st.subheader("Statistics")

    if st.session_state.transactions_df is not None:
        df = st.session_state.transactions_df

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Date Range",
                      f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")

        with col2:
            st.metric("Categories", len(df['Category'].unique()))

        with col3:
            st.metric("Unique Merchants", len(df['Description'].unique()))