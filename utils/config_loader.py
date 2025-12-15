"""Configuration loader for the RAG Knowledge Portal."""
import yaml
import os
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Load and manage configuration from YAML file."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self._ensure_directories()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        dirs = [
            self.config['app']['data_dir'],
            self.config['app']['documents_dir'],
            self.config['vector_db']['save_path'],
            os.path.dirname(self.config['logging']['file'])
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access."""
        return self.config[key]



