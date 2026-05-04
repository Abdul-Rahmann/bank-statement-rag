"""
Query Engine Module Handles both structured and semantic queries
"""

import re
from datetime import datetime, timedelta

import pandas as pd

from src.config import get_config_value


def _apply_time_filter(df, query_lower):
    """Apply time-based filtering. Returns (filtered_df, time_period_label)."""
    today = datetime.now()

    if 'last week' in query_lower or 'past week' in query_lower:
        week_ago = today - timedelta(days=7)
        return df[df['Date'] >= week_ago], "last week"
    elif 'last month' in query_lower or 'past month' in query_lower:
        month_ago = today - timedelta(days=30)
        return df[df['Date'] >= month_ago], "last month"
    elif 'this month' in query_lower or 'current month' in query_lower:
        return df[df['Date'].dt.month == today.month], "this month"
    elif 'this year' in query_lower or 'current year' in query_lower:
        return df[df['Date'].dt.year == today.year], "this year"
    elif 'last year' in query_lower:
        last_year = today.year - 1
        return df[df['Date'].dt.year == last_year], "last year"

    return df.copy(), "in your records"


def _apply_category_filter(df, query_lower):
    """Apply category-based filtering. Returns (filtered_df, matched_category)."""
    categories = get_config_value('CATEGORIES', {})
    for cat, keywords in categories.items():
        if any(keyword in query_lower for keyword in keywords):
            return df[df['Category'] == cat], cat
    return df.copy(), None


def _apply_type_filter(df, query_lower):
    """Apply transaction type filtering (withdrawal/deposit)."""
    if 'withdrawal' in query_lower or 'spent' in query_lower or 'paid' in query_lower:
        return df[df['Withdrawals ($)'] > 0]
    if 'deposit' in query_lower or 'received' in query_lower or 'income' in query_lower:
        return df[df['Deposits ($)'] > 0]
    return df.copy()


def _apply_amount_filter(df, query_lower):
    """Apply amount-based filtering from natural language."""
    under_match = re.search(r'under\s+\$?(\d+(?:\.\d{2})?)', query_lower)
    over_match = re.search(r'(?:over|above|more than)\s+\$?(\d+(?:\.\d{2})?)', query_lower)
    between_match = re.search(r'between\s+\$?(\d+(?:\.\d{2})?)\s+and\s+\$?(\d+(?:\.\d{2})?)', query_lower)
    lt_match = re.search(r'<\s*\$?(\d+(?:\.\d{2})?)', query_lower)
    gt_match = re.search(r'>\s*\$?(\d+(?:\.\d{2})?)', query_lower)

    if between_match:
        low, high = float(between_match.group(1)), float(between_match.group(2))
        return df[(df['Amount'] >= low) & (df['Amount'] <= high)]
    if under_match or lt_match:
        threshold = float((under_match or lt_match).group(1))
        return df[df['Amount'] < threshold]
    if over_match or gt_match:
        threshold = float((over_match or gt_match).group(1))
        return df[df['Amount'] > threshold]

    return df.copy()


def query_structured_data(query: str, df: pd.DataFrame) -> str:
    """
    Handle structured queries that require aggregations.
    Supports composable time, category, type, and amount filtering.
    """
    query_lower = query.lower()

    # Apply filters cumulatively
    filtered_df, time_period = _apply_time_filter(df, query_lower)
    filtered_df, category = _apply_category_filter(filtered_df, query_lower)
    filtered_df = _apply_type_filter(filtered_df, query_lower)
    filtered_df = _apply_amount_filter(filtered_df, query_lower)

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
