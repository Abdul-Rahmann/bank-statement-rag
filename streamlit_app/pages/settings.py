"""
Settings Page
System configuration and data management
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.resolve()
sys.path.append(str(root_dir))

import streamlit as st  # noqa: E402
import yaml  # noqa: E402

from src.config import get_config, get_safe_config  # noqa: E402
from streamlit_app.utils import (  # noqa: E402
    _save_chat_history,
    _save_chat_messages,
    initialize_rag,
)


def render():
    """Render the settings page."""
    st.header("Settings")

    # --- System Configuration (read-only) ---
    st.subheader("System Configuration")
    config = get_safe_config()
    if config:
        st.json(config)

    st.markdown("---")

    # --- Category Editor ---
    st.subheader("Categories")
    st.caption("Edit category keywords below. Changes are saved to config.yml.")

    categories = get_config().get('CATEGORIES', {})
    edited_categories = {}

    for category, keywords in categories.items():
        with st.expander(f"📁 {category}"):
            cols = st.columns([4, 1])
            with cols[0]:
                keywords_text = st.text_area(
                    "Keywords (one per line)",
                    value="\n".join(keywords),
                    key=f"cat_{category}",
                    height=100,
                    label_visibility="collapsed"
                )
            with cols[1]:
                if st.button("🗑️ Delete", key=f"del_{category}"):
                    # Remove from config and save immediately
                    config = get_config()
                    if 'CATEGORIES' in config and category in config['CATEGORIES']:
                        del config['CATEGORIES'][category]
                        _save_config(config)
                        _config_cache = None
                        st.success(f"Deleted category '{category}'")
                        st.rerun()
            edited_categories[category] = [k.strip() for k in keywords_text.splitlines() if k.strip()]

    # Add new category
    st.markdown("---")
    new_cat_name = st.text_input("New category name", key="new_cat_name")
    new_cat_keywords = st.text_area("Keywords (one per line)", key="new_cat_keywords", height=80)
    if st.button("➕ Add Category", key="add_cat"):
        if new_cat_name and new_cat_keywords:
            config = get_config()
            if 'CATEGORIES' not in config:
                config['CATEGORIES'] = {}
            config['CATEGORIES'][new_cat_name] = [k.strip() for k in new_cat_keywords.splitlines() if k.strip()]
            _save_config(config)
            _config_cache = None
            st.success(f"Added category '{new_cat_name}'")
            st.rerun()
        else:
            st.warning("Please enter both a category name and at least one keyword.")

    # Save & Re-categorize
    st.markdown("---")
    if st.button("💾 Save & Re-categorize", type="primary", key="save_cats"):
        # Build updated categories dict
        updated_categories = {}
        for category, keywords in edited_categories.items():
            if keywords:
                updated_categories[category] = keywords

        # Add new category if present
        new_name = st.session_state.get('new_cat_name', '')
        new_kw = st.session_state.get('new_cat_keywords', '')
        if new_name and new_kw:
            updated_categories[new_name] = [k.strip() for k in new_kw.splitlines() if k.strip()]

        config = get_config()
        config['CATEGORIES'] = updated_categories
        _save_config(config)
        _config_cache = None

        # Re-process transactions without re-extracting PDFs
        if st.session_state.transactions_df is not None:
            from src.processing import process_transactions
            df = st.session_state.transactions_df.copy()
            df = process_transactions(df)
            st.session_state.transactions_df = df
            st.success("Categories updated and transactions re-categorized!")
        else:
            st.success("Categories saved! Restart the assistant to apply changes.")
        st.rerun()

    st.markdown("---")

    # --- Data Management ---
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
            st.session_state.chat_messages = []
            _save_chat_history([])
            _save_chat_messages([])
            st.success("Chat history cleared!")

    st.markdown("---")

    # --- Statistics ---
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


def _save_config(config):
    """Write config dict back to config.yml."""
    from src.config import CONFIG_FILE_PATH
    with open(CONFIG_FILE_PATH, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
