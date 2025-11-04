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
        st.title("Financial Assistant")
        st.markdown("---")

        if st.session_state.rag is None:
            if st.button("Start Assistant", type="primary"):
                with st.spinner("Starting your AI assistant..."):
                    if initialize_rag():
                        st.success("Assistant started successfully!")
                        st.rerun()
        else:
            st.success("Assistant Working...")

            if st.session_state.transactions_df is not None:
                stats = st.session_state.rag.get_stats()
                st.markdown("### Quick Stats")
                st.metric("Transactions", f"{stats['total_transactions']:,}")
                st.metric("Total Spent", f"${stats['total_spent']:,.2f}")
                st.metric("Net", f"${stats['net']:,.2f}")

        st.markdown("---")

        st.markdown("### About")
        st.markdown("""
                This is your personal **AI financial assistant**, designed to help you manage your bank transactions and analyze your spending habits.

                ### Features
                - Dashboard with insightful visualizations and key metrics  
                - Chat interface to interact with your assistant  
                - Transaction history and detailed summaries  
                - Settings for a personalized experience 
                """)


def main():
    """Main application entry point."""
    setup_page()
    load_custom_css()
    initialize_session_state()

    render_sidebar()

    if st.session_state.rag is None:
        st.info("Please initialize your AI financial assistant using the init button on the sidebar.")
    else:
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