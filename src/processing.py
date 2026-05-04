"""Data Processing Module Cleans, enriches, and categorizes transaction data"""

import logging
import re

import numpy as np
import pandas as pd

from src.config import get_config_value

logger = logging.getLogger(__name__)


def _categorize_transactions(descriptions, categories):
    """Vectorized categorization of transaction descriptions."""
    desc_lower = descriptions.str.lower()
    conditions = []
    choices = []

    for category, keywords in categories.items():
        pattern = '|'.join(re.escape(kw) for kw in keywords)
        conditions.append(desc_lower.str.contains(pattern, regex=True, na=False))
        choices.append(category)

    return np.select(conditions, choices, default='other')


def process_transactions(df):
    """Clean and enrich transaction data."""
    # Parse dates
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Clean numeric columns
    df['Withdrawals ($)'] = pd.to_numeric(df['Withdrawals ($)'], errors='coerce').fillna(0)
    df['Deposits ($)'] = pd.to_numeric(df['Deposits ($)'], errors='coerce').fillna(0)
    df['Balance ($)'] = pd.to_numeric(df['Balance ($)'], errors='coerce').fillna(0)

    # Add computed columns
    df['Amount'] = df['Withdrawals ($)'] + df['Deposits ($)']
    df['Type'] = np.where(df['Deposits ($)'] > 0, 'Deposit', 'Withdrawal')
    df['Month'] = df['Date'].dt.to_period('M')
    df['Week'] = df['Date'].dt.to_period('W')
    df['Year'] = df['Date'].dt.year
    df['DayOfWeek'] = df['Date'].dt.day_name()

    # Add categories (vectorized, load config once)
    categories = get_config_value('CATEGORIES', {})
    df['Category'] = _categorize_transactions(df['Description'], categories)

    # Remove invalid dates
    df = df.dropna(subset=['Date'])

    # Sort by date
    df = df.sort_values('Date', ascending=False).reset_index(drop=True)

    return df


def get_summary_stats(df):
    """Get summary statistics for transactions."""
    if len(df) == 0:
        return {
            'total_transactions': 0,
            'total_spent': 0,
            'total_received': 0,
            'net': 0,
            'date_range': 'No data',
            'categories': {}
        }

    return {
        'total_transactions': len(df),
        'total_spent': df['Withdrawals ($)'].sum(),
        'total_received': df['Deposits ($)'].sum(),
        'net': df['Deposits ($)'].sum() - df['Withdrawals ($)'].sum(),
        'date_range': f"{df['Date'].min().strftime('%b %d, %Y')} to {df['Date'].max().strftime('%b %d, %Y')}",
        'categories': df['Category'].value_counts().to_dict()
    }


if __name__ == "__main__":
    # Test processing
    import sys

    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        df = pd.read_csv(csv_path)
        df = process_transactions(df)
        print(df.head())
        stats = get_summary_stats(df)
        print("Summary Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
