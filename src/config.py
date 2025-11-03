import os, sys
import yaml
import re
from dotenv import load_dotenv
from typing import Dict, Optional
from pathlib import Path

root_dir = Path(__file__).parent.parent.resolve()
CONFIG_FILE_PATH = root_dir / 'config.yml'

_config_cache: Optional[Dict] = None

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
        with open(os.getenv('CONFIG_FILE_PATH', CONFIG_FILE_PATH), 'r') as f:
            config = yaml.safe_load(f)
        _config_cache = _substitute_env_vars(config)
    return _config_cache

def get_config() -> Dict:
    """Get configuration."""
    return _load_config()

def get_config_value(key: str, default=None):
    """Get specific config value."""
    config = get_config()
    return config.get(key, default)

if __name__ == "__main__":
    config = get_config()
    print(get_config_value('OPENAI_API_KEY'))
