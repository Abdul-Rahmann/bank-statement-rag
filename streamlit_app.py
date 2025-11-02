"""
Streamlit Web Interface for Bank Statement RAG Bot
Interactive dashboard with visualizations and chat interface
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

from src.rag_system import BankStatementRAG

# Page config
st.set_page_config(
    page_title="Bank Statement RAG Bot",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag' not in st.session_state:
    st.session_state.rag = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'transactions_df' not in st.session_state:
    st.session_state.transactions_df = None

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

def create_spending_over_time_chart(df, time_period='M'):
    """Create spending over time line chart."""
    df_copy = df.copy()

    if time_period == 'D':
        df_copy['Period'] = df_copy['Date'].dt.date
        title = "Daily Spending"
    elif time_period == 'W':
        df_copy['Period'] = df_copy['Date'].dt.to_period('W').astype(str)
        title = "Weekly Spending"
    elif time_period == 'M':
        df_copy['Period'] = df_copy['Date'].dt.to_period('M').astype(str)
        title = "Monthly Spending"
    else:
        df_copy['Period'] = df_copy['Date'].dt.to_period('Y').astype(str)
        title = "Yearly Spending"

    spending_data = df_copy.groupby('Period').agg({
        'Withdrawals ($)': 'sum',
        'Deposits ($)': 'sum'
    }).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spending_data['Period'],
        y=spending_data['Withdrawals ($)'],
        name='Spending',
        mode='lines+markers',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=spending_data['Period'],
        y=spending_data['Deposits ($)'],
        name='Income',
        mode='lines+markers',
        line=dict(color='#4ECDC4', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Period",
        yaxis_title="Amount ($)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig

def create_category_breakdown_chart(df):
    """Create category breakdown pie chart."""
    category_data = df.groupby('Category')['Withdrawals ($)'].sum().reset_index()
    category_data = category_data.sort_values('Withdrawals ($)', ascending=False)

    fig = px.pie(
        category_data,
        values='Withdrawals ($)',
        names='Category',
        title='Spending by Category',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>'
    )

    fig.update_layout(height=400)

    return fig

def create_top_merchants_chart(df, top_n=10):
    """Create top merchants bar chart."""
    merchant_data = df.groupby('Description')['Withdrawals ($)'].sum().reset_index()
    merchant_data = merchant_data.sort_values('Withdrawals ($)', ascending=False).head(top_n)

    fig = px.bar(
        merchant_data,
        x='Withdrawals ($)',
        y='Description',
        orientation='h',
        title=f'Top {top_n} Merchants by Spending',
        color='Withdrawals ($)',
        color_continuous_scale='Reds'
    )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Total Spent ($)",
        yaxis_title="Merchant",
        height=400,
        showlegend=False
    )

    return fig

def create_transaction_heatmap(df):
    """Create transaction heatmap by day of week and hour."""
    df_copy = df.copy()
    df_copy['DayOfWeek'] = df_copy['Date'].dt.day_name()
    df_copy['Month'] = df_copy['Date'].dt.month_name()

    heatmap_data = df_copy.groupby(['Month', 'DayOfWeek']).size().reset_index(name='Count')

    # Pivot for heatmap
    pivot_data = heatmap_data.pivot(index='DayOfWeek', columns='Month', values='Count').fillna(0)

    # Order days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_data = pivot_data.reindex(day_order)

    fig = px.imshow(
        pivot_data,
        title='Transaction Frequency Heatmap',
        labels=dict(x="Month", y="Day of Week", color="Transactions"),
        color_continuous_scale='Blues',
        aspect='auto'
    )

    fig.update_layout(height=400)

    return fig

def render_dashboard():
    """Render the main dashboard tab."""
    st.markdown('<p class="main-header">Dashboard</p>', unsafe_allow_html=True)

    if st.session_state.transactions_df is None:
        st.warning("No data loaded. Please initialize the system first.")
        return

    df = st.session_state.transactions_df

    # Get statistics
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

def render_chat():
    """Render the chat interface tab."""
    st.markdown('<p class="main-header">Chat Assistant</p>', unsafe_allow_html=True)

    if st.session_state.rag is None:
        st.warning("Please initialize the system first.")
        return

    # Chat history
    chat_container = st.container()

    with chat_container:
        for idx, message in enumerate(st.session_state.chat_history):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "chart" in message:
                    st.plotly_chart(message["chart"], use_container_width=True, key=f"chat_chart_{idx}")

    # Chat input
    if prompt := st.chat_input("Ask about your transactions..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.rag.ask(prompt)
                st.markdown(response)

                # Check if query needs a visualization
                chart = generate_chart_for_query(prompt, st.session_state.transactions_df)
                if chart:
                    chart_idx = len(st.session_state.chat_history)
                    st.plotly_chart(chart, use_container_width=True, key=f"chat_chart_{chart_idx}")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "chart": chart
                    })
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

def generate_chart_for_query(query, df):
    """Generate appropriate chart based on query."""
    query_lower = query.lower()

    # Category breakdown queries
    if any(word in query_lower for word in ['category', 'breakdown', 'categories']):
        return create_category_breakdown_chart(df)

    # Time-based spending queries
    if any(word in query_lower for word in ['over time', 'trend', 'monthly', 'weekly']):
        if 'week' in query_lower:
            return create_spending_over_time_chart(df, 'W')
        elif 'day' in query_lower:
            return create_spending_over_time_chart(df, 'D')
        else:
            return create_spending_over_time_chart(df, 'M')

    # Top merchants queries
    if any(word in query_lower for word in ['top', 'most', 'largest', 'biggest']):
        if 'merchant' in query_lower or 'store' in query_lower or 'where' in query_lower:
            return create_top_merchants_chart(df)

    return None

def render_transactions():
    """Render the transactions browser tab."""
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
    display_df = filtered_df[['Date', 'Description', 'Category', 'Withdrawals ($)', 'Deposits ($)', 'Balance ($)']].copy()
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

def render_settings():
    """Render the settings tab."""
    st.markdown('<p class="main-header">Settings</p>', unsafe_allow_html=True)

    st.subheader("System Configuration")

    config = load_config()
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
            st.metric("Date Range", f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")

        with col2:
            st.metric("Categories", len(df['Category'].unique()))

        with col3:
            st.metric("Unique Merchants", len(df['Description'].unique()))

def main():
    """Main application."""

    # Sidebar
    with st.sidebar:
        st.title("Bank Statement RAG Bot")
        st.markdown("---")

        # Initialize button
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

    # Main content
    if st.session_state.rag is None:
        st.info("Please initialize the system using the sidebar.")
    else:
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Chat", "Transactions", "Settings"])

        with tab1:
            render_dashboard()

        with tab2:
            render_chat()

        with tab3:
            render_transactions()

        with tab4:
            render_settings()

if __name__ == "__main__":
    main()