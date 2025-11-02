"""
Chart Creation Functions
All Plotly chart generation functions
"""

import plotly.express as px
import plotly.graph_objects as go


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
    """Create transaction heatmap by day of week and month."""
    df_copy = df.copy()
    df_copy['DayOfWeek'] = df_copy['Date'].dt.day_name()
    df_copy['Month'] = df_copy['Date'].dt.month_name()

    heatmap_data = df_copy.groupby(['Month', 'DayOfWeek']).size().reset_index(name='Count')
    pivot_data = heatmap_data.pivot(index='DayOfWeek', columns='Month', values='Count').fillna(0)

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


def generate_chart_for_query(query, df):
    """Generate appropriate chart based on query keywords."""
    query_lower = query.lower()

    if any(word in query_lower for word in ['category', 'breakdown', 'categories']):
        return create_category_breakdown_chart(df)

    if any(word in query_lower for word in ['over time', 'trend', 'monthly', 'weekly']):
        if 'week' in query_lower:
            return create_spending_over_time_chart(df, 'W')
        elif 'day' in query_lower:
            return create_spending_over_time_chart(df, 'D')
        else:
            return create_spending_over_time_chart(df, 'M')

    if any(word in query_lower for word in ['top', 'most', 'largest', 'biggest']):
        if 'merchant' in query_lower or 'store' in query_lower or 'where' in query_lower:
            return create_top_merchants_chart(df)

    return None
