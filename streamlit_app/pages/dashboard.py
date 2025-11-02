"""
Dashboard Page
Main dashboard with visualizations and metrics
"""

import streamlit as st
from streamlit_app.charts import (
    create_spending_over_time_chart,
    create_category_breakdown_chart,
    create_top_merchants_chart,
    create_transaction_heatmap
)


def render():
    """Render the dashboard page."""
    st.markdown('<p class="main-header">Dashboard</p>', unsafe_allow_html=True)

    if st.session_state.transactions_df is None:
        st.warning("No data loaded. Please initialize the system first.")
        return

    df = st.session_state.transactions_df
    stats = st.session_state.rag.get_stats()

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Transactions",
            value=f"{stats['total_transactions']:,}"
        )

    with col2:
        st.metric(
            label="Total Spent",
            value=f"${stats['total_spent']:,.2f}",
            delta=None
        )

    with col3:
        st.metric(
            label="Total Received",
            value=f"${stats['total_received']:,.2f}",
            delta=None
        )

    with col4:
        net_color = "normal" if stats['net'] >= 0 else "inverse"
        st.metric(
            label="Net",
            value=f"${stats['net']:,.2f}",
            delta=f"${stats['net']:,.2f}" if stats['net'] >= 0 else f"-${abs(stats['net']):,.2f}"
        )

    st.markdown("---")

    # Time period selector
    col1, col2 = st.columns([1, 4])
    with col1:
        time_period = st.selectbox(
            "Time Period",
            options=['D', 'W', 'M', 'Y'],
            format_func=lambda x: {'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly', 'Y': 'Yearly'}[x],
            index=2
        )

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            create_spending_over_time_chart(df, time_period),
            use_container_width=True,
            key="dashboard_spending_time"
        )

    with col2:
        st.plotly_chart(
            create_category_breakdown_chart(df),
            use_container_width=True,
            key="dashboard_category_breakdown"
        )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            create_top_merchants_chart(df),
            use_container_width=True,
            key="dashboard_top_merchants"
        )

    with col2:
        st.plotly_chart(
            create_transaction_heatmap(df),
            use_container_width=True,
            key="dashboard_heatmap"
        )