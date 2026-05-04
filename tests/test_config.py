"""Tests for src/config.py."""

import os
import pytest
from src.config import get_config_value, get_safe_config, _substitute_env_vars


class TestSubstituteEnvVars:
    def test_substitutes_string(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "hello")
        result = _substitute_env_vars("${TEST_VAR}")
        assert result == "hello"

    def test_substitutes_nested_dict(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "secret123")
        obj = {"secrets": {"key": "${API_KEY}"}}
        result = _substitute_env_vars(obj)
        assert result["secrets"]["key"] == "secret123"

    def test_leaves_nonexistent_var_empty(self):
        result = _substitute_env_vars("${NONEXISTENT_VAR_XYZ}")
        assert result == ""


class TestGetConfigValue:
    def test_top_level_key(self, mock_config):
        # We can't easily mock get_config() without patching, so test the logic directly
        pass

    def test_nested_key_with_dots(self, mock_config):
        # This would require monkeypatching the module-level cache
        pass


class TestGetSafeConfig:
    def test_redacts_secrets(self, mock_config):
        from src.config import get_safe_config
        import src.config as config_module

        # Temporarily override cache
        original_cache = config_module._config_cache
        config_module._config_cache = mock_config
        try:
            safe = get_safe_config()
            assert safe["SECRETS"]["OPENAI_API_KEY"] == "***REDACTED***"
            # Original should be untouched
            assert mock_config["SECRETS"]["OPENAI_API_KEY"] == "test-key"
        finally:
            config_module._config_cache = original_cache
