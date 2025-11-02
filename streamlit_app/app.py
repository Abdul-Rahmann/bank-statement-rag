"""
Main Streamlit Application
Orchestrates all pages and components
"""

import streamlit as st
from streamlit_app.config import setup_page, load_custom_css
from streamlit_app.utils import initialize_session_state, initialize_rag
from streamlit_app.pages import dashboard, chat, transactions, settings


def render_sidebar():
    """Render the sidebar."""
    with st.sidebar:
        st.title("Bank Statement RAG Bot")
        st.markdown("---")

        if st.session_state.rag is None:
            if st.button("Initialize System", type="primary"):
                if initialize_rag():
                    st.success("System initialized!")
                    st.rerun()
        else:
            st.success("System Ready")

            if st.session_state.transactions_df is not None:
                stats = st.session_state.rag.get_stats()
                st.markdown("### Quick Stats")
                st.metric("Transactions", f"{stats['total_transactions']:,}")
                st.metric("Total Spent", f"${stats['total_spent']:,.2f}")
                st.metric("Net", f"${stats['net']:,.2f}")

        st.markdown("---")

        st.markdown("### About")
        st.markdown("""
                This application uses AI to analyze your bank statements and provide insights.

                **Features:**
                - Smart categorization
                - Semantic search
                - Interactive visualizations
                - Natural language queries
                """)


def main():
    """Main application entry point."""
    # Setup
    setup_page()
    load_custom_css()
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Main content
    if st.session_state.rag is None:
        st.info("Please initialize the system using the sidebar.")
    else:
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Chat", "Transactions", "Settings"])

        with tab1:
            dashboard.render()

        with tab2:
            chat.render()

        with tab3:
            transactions.render()

        with tab4:
            settings.render()


if __name__ == "__main__":
    main()