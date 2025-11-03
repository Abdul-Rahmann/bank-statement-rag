"""Data Processing Module Cleans, enriches, and categorizes transaction data"""

import pandas as pd
from src.config import get_config_value


def categorize_transaction(description):
    """Categorize transactions based on merchant/description."""
    if pd.isna(description):
        return 'other'

    desc_lower = description.lower()
    categories = get_config_value('CATEGORIES')

    for category, keywords in categories.items():
        if any(keyword in desc_lower for keyword in keywords):
            return category

    return 'other'


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
    df['Type'] = df.apply(lambda x: 'Deposit' if x['Deposits ($)'] > 0 else 'Withdrawal', axis=1)
    df['Month'] = df['Date'].dt.to_period('M')
    df['Week'] = df['Date'].dt.to_period('W')
    df['Year'] = df['Date'].dt.year
    df['DayOfWeek'] = df['Date'].dt.day_name()

    # Add categories
    df['Category'] = df['Description'].apply(categorize_transaction)

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
