"""
Utility Functions
Helper functions for the Streamlit app
"""

import json
import sys
from pathlib import Path

import streamlit as st

root_dir = Path(__file__).parent.parent.parent.resolve()
sys.path.append(str(root_dir))

from src.config import get_config  # noqa: E402
from src.rag_system import BankStatementRAG  # noqa: E402

CHAT_HISTORY_PATH = root_dir / 'data' / 'chat_history.json'
MAX_CHAT_MESSAGES = 100


def _load_chat_history():
    """Load chat history from disk."""
    if CHAT_HISTORY_PATH.exists():
        try:
            with open(CHAT_HISTORY_PATH) as f:
                history = json.load(f)
            for msg in history:
                msg.pop('chart', None)
            return history[-MAX_CHAT_MESSAGES:]
        except Exception:
            return []
    return []


def _save_chat_history(history):
    """Save chat history to disk."""
    CHAT_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    serializable = []
    for msg in history[-MAX_CHAT_MESSAGES:]:
        msg_copy = {k: v for k, v in msg.items() if k != 'chart'}
        serializable.append(msg_copy)
    try:
        with open(CHAT_HISTORY_PATH, 'w') as f:
            json.dump(serializable, f)
    except Exception:
        pass


@st.cache_data(ttl=3600)
def cached_get_summary_stats(df):
    """Cached wrapper for summary stats to avoid recomputation on every render."""
    from src.processing import get_summary_stats
    return get_summary_stats(df)


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
        st.session_state.chat_history = _load_chat_history()
    if 'transactions_df' not in st.session_state:
        st.session_state.transactions_df = None
