"""
Dashboard Page
Main dashboard with visualizations and metrics
"""

import streamlit as st

from streamlit_app.charts import (
    create_category_breakdown_chart,
    create_spending_over_time_chart,
    create_top_merchants_chart,
    create_transaction_heatmap,
)
from streamlit_app.utils import cached_get_summary_stats


def render():
    """Render the dashboard page."""
    st.header("Dashboard")

    if st.session_state.transactions_df is None:
        st.warning("No data loaded. Please initialize the system first.")
        return

    df = st.session_state.transactions_df
    stats = cached_get_summary_stats(df)

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
        fig1 = create_spending_over_time_chart(df, time_period)
        st.plotly_chart(fig1, use_container_width=True, key="dashboard_spending_time")
        st.download_button(
            label="📥 Download PNG",
            data=fig1.to_image(format="png", scale=2),
            file_name="spending_over_time.png",
            mime="image/png",
            key="download_spending_time"
        )

    with col2:
        fig2 = create_category_breakdown_chart(df)
        st.plotly_chart(fig2, use_container_width=True, key="dashboard_category_breakdown")
        st.download_button(
            label="📥 Download PNG",
            data=fig2.to_image(format="png", scale=2),
            file_name="category_breakdown.png",
            mime="image/png",
            key="download_category_breakdown"
        )

    col1, col2 = st.columns(2)

    with col1:
        fig3 = create_top_merchants_chart(df)
        st.plotly_chart(fig3, use_container_width=True, key="dashboard_top_merchants")
        st.download_button(
            label="📥 Download PNG",
            data=fig3.to_image(format="png", scale=2),
            file_name="top_merchants.png",
            mime="image/png",
            key="download_top_merchants"
        )

    with col2:
        fig4 = create_transaction_heatmap(df)
        st.plotly_chart(fig4, use_container_width=True, key="dashboard_heatmap")
        st.download_button(
            label="📥 Download PNG",
            data=fig4.to_image(format="png", scale=2),
            file_name="transaction_heatmap.png",
            mime="image/png",
            key="download_heatmap"
        )
