"""
Transactions Page
Browse and filter ransactions
"""

import streamlit as st
from datetime import datetime


def render():
    """Render the transactions page."""
    st.markdown('<p class="main-header">Transaction Browser</p>', unsafe_allow_html=True)

    if st.session_state.transactions_df is None:
        st.warning("No data loaded. Please initialize the system first.")
        return

    df = st.session_state.transactions_df

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        categories = ['All'] + sorted(df['Category'].unique().tolist())
        selected_category = st.selectbox("Category", categories)

    with col2:
        transaction_types = ['All', 'Withdrawal', 'Deposit']
        selected_type = st.selectbox("Type", transaction_types)

    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(df['Date'].min(), df['Date'].max()),
            min_value=df['Date'].min().date(),
            max_value=df['Date'].max().date()
        )

    # Apply filters
    filtered_df = df.copy()

    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]

    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['Type'] == selected_type]

    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['Date'].dt.date >= date_range[0]) &
            (filtered_df['Date'].dt.date <= date_range[1])
            ]

    # Summary
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} transactions**")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Spent", f"${filtered_df['Withdrawals ($)'].sum():,.2f}")
    with col2:
        st.metric("Total Received", f"${filtered_df['Deposits ($)'].sum():,.2f}")

    st.markdown("---")

    # Transaction table
    display_df = filtered_df[
        ['Date', 'Description', 'Category', 'Withdrawals ($)', 'Deposits ($)', 'Balance ($)']].copy()
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
        hide_index=True
    )

    # Export
    col1, col2 = st.columns([1, 4])
    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export to CSV",
            data=csv,
            file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )