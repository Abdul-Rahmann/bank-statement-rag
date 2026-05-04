import copy
import os
import re
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

root_dir = Path(__file__).parent.parent.resolve()
CONFIG_FILE_PATH = root_dir / 'config.yml'

_config_cache: dict | None = None


def _substitute_env_vars(obj):
    """Recursively replace ${VAR} in dict/list/str with environment variable."""
    pattern = re.compile(r'\$\{([^}]+)\}')
    if isinstance(obj, dict):
        return {k: _substitute_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_substitute_env_vars(i) for i in obj]
    elif isinstance(obj, str):
        matches = pattern.findall(obj)
        for var in matches:
            env_val = os.getenv(var, '')
            obj = obj.replace(f"${{{var}}}", env_val)
        return obj
    else:
        return obj


def _load_config():
    """Load configuration from a YAML file and replace env vars."""
    global _config_cache
    if _config_cache is None:
        load_dotenv()
        config_path = os.getenv('CONFIG_FILE_PATH', CONFIG_FILE_PATH)
        with open(config_path) as f:
            config = yaml.safe_load(f)
        _config_cache = _substitute_env_vars(config)
    return _config_cache


def get_config() -> dict:
    """Get configuration."""
    return _load_config()


def get_config_value(key: str, default=None) -> Any:
    """Get specific config value.

    Supports dot-notation for nested keys, e.g. 'PATHS.DATA_DIR'.
    Falls back to top-level lookup for backwards compatibility.
    """
    config = get_config()
    if '.' in key:
        parts = key.split('.')
        value = config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return value
    return config.get(key, default)


def get_safe_config() -> dict:
    """Return a copy of config with SECRETS redacted."""
    config = copy.deepcopy(get_config())
    if 'SECRETS' in config and isinstance(config['SECRETS'], dict):
        for secret_key in config['SECRETS']:
            config['SECRETS'][secret_key] = '***REDACTED***'
    return config


if __name__ == "__main__":
    config = get_config()
    print(get_config_value('PATHS.DATA_DIR'))
