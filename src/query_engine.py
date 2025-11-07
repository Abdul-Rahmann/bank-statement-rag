"""
Query Engine Module Handles both structured and semantic queries
"""

import pandas as pd
from datetime import datetime, timedelta
from src.config import get_config, get_config_value

def query_structured_data(query: str, df: pd.DataFrame) -> str:
    """
    Handle structured queries that require aggregations.
    Supports time filtering, category filtering, and various aggregation types.
    """
    query_lower = query.lower()
    today = datetime.now()

    # Filter by time period
    filtered_df = df.copy()
    time_period = "in your records"

    if 'last week' in query_lower or 'past week' in query_lower:
        week_ago = today - timedelta(days=7)
        filtered_df = df[df['Date'] >= week_ago]
        time_period = "last week"
    elif 'last month' in query_lower or 'past month' in query_lower:
        month_ago = today - timedelta(days=30)
        filtered_df = df[df['Date'] >= month_ago]
        time_period = "last month"
    elif 'this month' in query_lower or 'current month' in query_lower:
        filtered_df = df[df['Date'].dt.month == today.month]
        time_period = "this month"
    elif 'this year' in query_lower or 'current year' in query_lower:
        filtered_df = df[df['Date'].dt.year == today.year]
        time_period = "this year"
    elif 'last year' in query_lower:
        last_year = today.year - 1
        filtered_df = df[df['Date'].dt.year == last_year]
        time_period = "last year"

    # Filter by category
    category = None
    category_keywords = get_config_value('CATEGORIES')

    for cat, keywords in category_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            category = cat
            filtered_df = filtered_df[filtered_df['Category'] == category]
            break

    # Filter by transaction type
    if 'withdrawal' in query_lower or 'spent' in query_lower or 'paid' in query_lower:
        filtered_df = filtered_df[filtered_df['Withdrawals ($)'] > 0]
    elif 'deposit' in query_lower or 'received' in query_lower or 'income' in query_lower:
        filtered_df = filtered_df[filtered_df['Deposits ($)'] > 0]

    if filtered_df.empty:
        return f"No transactions found {time_period}" + (f" for {category}" if category else "")

    # Handle different query types
    if any(word in query_lower for word in ['total', 'sum', 'how much', 'amount']):
        return _format_total_response(filtered_df, time_period, category, query_lower)
    elif 'average' in query_lower or 'mean' in query_lower:
        return _format_average_response(filtered_df, time_period, category)
    elif 'largest' in query_lower or 'biggest' in query_lower or 'most expensive' in query_lower or 'highest' in query_lower:
        return _format_largest_response(filtered_df, time_period)
    elif 'smallest' in query_lower or 'lowest' in query_lower:
        return _format_smallest_response(filtered_df, time_period)
    elif 'count' in query_lower or 'how many' in query_lower or 'number' in query_lower:
        return _format_count_response(filtered_df, time_period, category)
    elif 'breakdown' in query_lower or 'category' in query_lower or 'categories' in query_lower:
        return _format_breakdown_response(filtered_df, time_period)

    # Default: return recent transactions
    return _format_recent_response(filtered_df, time_period, category)

def _format_total_response(df, time_period, category, query_lower):
    """Format response for total/sum queries."""
    total_spent = df['Withdrawals ($)'].sum()
    total_received = df['Deposits ($)'].sum()
    count = len(df)

    result = f"💰 **Summary {time_period}"
    if category:
        result += f" for {category}"
    result += ":**\n\n"

    if 'spent' in query_lower or 'withdrawal' in query_lower or category:
        result += f"Total spent: ${total_spent:,.2f}\n"
        result += f"Number of transactions: {count}\n"
        if count > 0:
            result += f"Average per transaction: ${total_spent/count:,.2f}\n\n"
    elif 'deposit' in query_lower or 'received' in query_lower:
        result += f"Total received: ${total_received:,.2f}\n"
        result += f"Number of transactions: {count}\n\n"
    else:
        result += f"Total spent: ${total_spent:,.2f}\n"
        result += f"Total received: ${total_received:,.2f}\n"
        result += f"Net: ${total_received - total_spent:,.2f}\n"
        result += f"Number of transactions: {count}\n\n"

    # Show top transactions
    result += "**Top transactions:**\n"
    top_transactions = df.nlargest(5, 'Amount')[['Date', 'Description', 'Amount']]
    for _, row in top_transactions.iterrows():
        result += f"• {row['Date'].strftime('%b %d, %Y')}: ${row['Amount']:,.2f} at {row['Description']}\\n"

    return result

def _format_average_response(df, time_period, category):
    """Format response for average queries."""
    avg_spent = df['Withdrawals ($)'].mean()
    result = f"Average spent {time_period}"
    if category:
        result += f" on {category}"
    result += f": ${avg_spent:,.2f}"
    return result

def _format_largest_response(df, time_period):
    """Format response for largest transaction queries."""
    largest = df.nlargest(5, 'Amount')
    result = f"**Largest transactions {time_period}:**\n\n"
    for _, row in largest.iterrows():
        result += f"• {row['Date'].strftime('%b %d, %Y')}: ${row['Amount']:,.2f} at {row['Description']}\n"
    return result

def _format_smallest_response(df, time_period):
    """Format response for smallest transaction queries."""
    smallest = df[df['Amount'] > 0].nsmallest(5, 'Amount')
    result = f"**Smallest transactions {time_period}:**\n\n"
    for _, row in smallest.iterrows():
        result += f"• {row['Date'].strftime('%b %d, %Y')}: ${row['Amount']:,.2f} at {row['Description']}\n"
    return result

def _format_count_response(df, time_period, category):
    """Format response for count queries."""
    count = len(df)
    result = f"You made {count} transactions {time_period}"
    if category:
        result += f" in the {category} category"
    return result

def _format_breakdown_response(df, time_period):
    """Format response for category breakdown queries."""
    category_breakdown = df.groupby('Category')['Withdrawals ($)'].sum().sort_values(ascending=False)
    result = f"**Category breakdown {time_period}:**\n\n"
    total = df['Withdrawals ($)'].sum()
    for cat, amount in category_breakdown.items():
        percentage = (amount / total) * 100 if total > 0 else 0
        result += f"• {cat.title()}: ${amount:,.2f} ({percentage:.1f}%)\n"
    return result

def _format_recent_response(df, time_period, category):
    """Format response showing recent transactions."""
    result = f"**Recent transactions {time_period}"
    if category:
        result += f" - {category}"
    result += ":**\n\n"

    recent = df.head(10)[['Date', 'Description', 'Amount', 'Balance ($)']]
    for _, row in recent.iterrows():
        result += f"• {row['Date'].strftime('%b %d, %Y')}: ${row['Amount']:,.2f} at {row['Description']} (Balance: ${row['Balance ($)']:,.2f})\n"

    return result

def semantic_search(vectorstore, query: str, k: int = 5) -> str:
    """Search for specific transactions using semantic similarity."""
    docs = vectorstore.similarity_search(query, k=k)
    result = "**Relevant transactions:**\n\n"
    for doc in docs:
        result += doc.page_content + "\n\n"
    return result

if __name__ == "__main__":
    ...