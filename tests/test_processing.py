"""Tests for src/processing.py."""

import pandas as pd
import numpy as np
from src.processing import process_transactions, get_summary_stats, _categorize_transactions


class TestCategorizeTransactions:
    def test_matches_keywords(self):
        descriptions = pd.Series(["Starbucks Coffee", "Walmart Grocery", "Unknown Merchant"])
        categories = {
            "dining": ["starbucks", "coffee"],
            "groceries": ["walmart", "grocery"],
        }
        result = _categorize_transactions(descriptions, categories)
        assert result[0] == "dining"
        assert result[1] == "groceries"
        assert result[2] == "other"

    def test_first_match_wins(self):
        descriptions = pd.Series(["Starbucks Grocery"])
        categories = {
            "dining": ["starbucks"],
            "groceries": ["grocery"],
        }
        result = _categorize_transactions(descriptions, categories)
        assert result[0] == "dining"


class TestProcessTransactions:
    def test_adds_computed_columns(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        assert "Amount" in df.columns
        assert "Type" in df.columns
        assert "Category" in df.columns
        assert "Month" in df.columns
        assert "Year" in df.columns

    def test_categorizes_correctly(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        # Find by description since DataFrame is sorted by date descending
        groceries = df[df["Description"] == "Grocery Store Purchase"]
        dining = df[df["Description"] == "Starbucks Coffee"]
        assert groceries.iloc[0]["Category"] == "groceries"
        assert dining.iloc[0]["Category"] == "dining"

    def test_sorts_descending_by_date(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        assert df.iloc[0]["Date"] >= df.iloc[1]["Date"]


class TestGetSummaryStats:
    def test_empty_dataframe(self):
        df = pd.DataFrame()
        stats = get_summary_stats(df)
        assert stats["total_transactions"] == 0
        assert stats["total_spent"] == 0

    def test_computes_correctly(self, sample_transactions_df):
        import pytest
        df = process_transactions(sample_transactions_df)
        stats = get_summary_stats(df)
        assert stats["total_transactions"] == 6
        assert stats["total_spent"] == pytest.approx(243.10, 0.01)
        assert stats["total_received"] == pytest.approx(3000.00, 0.01)
