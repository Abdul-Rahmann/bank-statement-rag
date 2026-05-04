"""Shared test fixtures."""

import pytest
import pandas as pd
from datetime import datetime


@pytest.fixture
def sample_transactions_df():
    """Return a sample DataFrame for testing."""
    return pd.DataFrame({
        "Date": pd.to_datetime([
            "2024-01-15", "2024-01-20", "2024-02-10",
            "2024-02-15", "2024-03-01", "2024-03-05"
        ]),
        "Description": [
            "Grocery Store Purchase", "Starbucks Coffee", "Amazon Order",
            "Gym Membership", "Salary Deposit", "Uber Ride"
        ],
        "Withdrawals ($)": [45.50, 5.20, 120.00, 50.00, 0.00, 23.40],
        "Deposits ($)": [0.00, 0.00, 0.00, 0.00, 3000.00, 0.00],
        "Balance ($)": [954.50, 949.30, 829.30, 779.30, 3779.30, 3755.90],
    })


@pytest.fixture
def mock_config():
    """Return a mock configuration dict."""
    return {
        "CATEGORIES": {
            "groceries": ["grocery", "safeway", "walmart", "groceries"],
            "dining": ["restaurant", "starbucks", "coffee"],
            "shopping": ["amazon", "ebay"],
            "fitness": ["gym", "fitness"],
            "transportation": ["uber", "lyft"],
        },
        "PATHS": {
            "DATA_DIR": "data/raw",
            "PROCESSED_DIR": "data/processed",
            "VECTORS_DIR": "data/vectors/vectorstore",
            "TRANSACTIONS_CSV": "data/processed/transactions.csv",
        },
        "SECRETS": {
            "OPENAI_API_KEY": "test-key",
        },
        "MODEL": {
            "name": "gpt-4o-mini",
            "temperature": 0,
        },
        "EXTRACTION": {
            "DEPOSIT_TRIGGERS": ["Deposit", "MB-Transferfrom"],
        },
    }
