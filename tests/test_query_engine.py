"""Tests for src/query_engine.py."""

import pandas as pd
from datetime import datetime, timedelta
from src.query_engine import (
    _apply_time_filter,
    _apply_category_filter,
    _apply_type_filter,
    _apply_amount_filter,
    query_structured_data,
)
from src.processing import process_transactions


class TestApplyTimeFilter:
    def test_last_week(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        # All sample dates are in the past, so this should return empty
        filtered, label = _apply_time_filter(df, "show me last week")
        assert label == "last week"

    def test_this_year(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        filtered, label = _apply_time_filter(df, "show me this year")
        assert label == "this year"
        # All sample dates are from 2024, so if current year is 2024+ this is empty


class TestApplyCategoryFilter:
    def test_matches_groceries(self, sample_transactions_df, mock_config):
        import src.query_engine as qe
        original = qe.get_config_value
        qe.get_config_value = lambda key, default=None: mock_config.get("CATEGORIES", default) if key == "CATEGORIES" else default
        try:
            df = process_transactions(sample_transactions_df)
            filtered, category = _apply_category_filter(df, "groceries spending")
            assert category == "groceries"
            assert all(filtered["Category"] == "groceries")
        finally:
            qe.get_config_value = original

    def test_no_match_returns_all(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        filtered, category = _apply_category_filter(df, "xyz nonsense")
        assert category is None
        assert len(filtered) == len(df)


class TestApplyTypeFilter:
    def test_withdrawals_only(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        filtered = _apply_type_filter(df, "withdrawals")
        assert all(filtered["Withdrawals ($)"] > 0)

    def test_deposits_only(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        filtered = _apply_type_filter(df, "deposits")
        assert all(filtered["Deposits ($)"] > 0)


class TestApplyAmountFilter:
    def test_under_threshold(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        filtered = _apply_amount_filter(df, "under $50")
        assert all(filtered["Amount"] < 50)

    def test_over_threshold(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        filtered = _apply_amount_filter(df, "over 100")
        assert all(filtered["Amount"] > 100)

    def test_between_thresholds(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        filtered = _apply_amount_filter(df, "between 20 and 100")
        assert all((filtered["Amount"] >= 20) & (filtered["Amount"] <= 100))


class TestQueryStructuredData:
    def test_total_query(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        response = query_structured_data("total spent", df)
        assert "$" in response
        assert "Summary" in response

    def test_count_query(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        response = query_structured_data("how many transactions", df)
        assert "6" in response or "transactions" in response
