"""Configuration management for Ultron"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """Configuration loader and accessor"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            content = f.read()
            # Expand environment variables
            content = os.path.expandvars(content)
            self._config = yaml.safe_load(content)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'telegram.bot_token')"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access"""
        return self.get(key)

    def __contains__(self, key: str) -> bool:
        """Check if key exists"""
        return self.get(key) is not None


# Global config instance
_config: Config | None = None


def get_config(config_path: str = "config.yaml") -> Config:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
