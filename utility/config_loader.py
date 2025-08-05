#!/usr/bin/env python3
"""
Configuration loader for YAML-based configuration with environment variable support
"""

import os
import yaml
import logging
from typing import Dict, Any
from pathlib import Path

class ConfigLoader:
    """Configuration loader that supports YAML files with environment variable substitution"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize config loader
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and parse YAML configuration with environment variable substitution"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                yaml_content = f.read()
            
            # Replace environment variables in YAML content
            processed_content = self._replace_env_vars(yaml_content)
            
            # Parse YAML
            config = yaml.safe_load(processed_content)
            
            logging.info(f"Configuration loaded from {self.config_path}")
            return config
            
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML configuration: {e}")
            raise
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            raise
    
    def _replace_env_vars(self, content: str) -> str:
        """Replace environment variable placeholders in YAML content"""
        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        import re
        # Replace ${VAR_NAME} patterns with environment variable values
        return re.sub(r'\$\{([^}]+)\}', replace_var, content)
    
    def get_openai_config(self, agent_type: str) -> Dict[str, Any]:
        """
        Get OpenAI configuration for specific agent type
        
        Args:
            agent_type: Either 'policy_agent' or 'utility_agent'
            
        Returns:
            OpenAI configuration dictionary
        """
        if 'openai' not in self.config:
            raise KeyError("OpenAI configuration not found in config file")
        
        if agent_type not in self.config['openai']:
            raise KeyError(f"Configuration for agent type '{agent_type}' not found")
        
        return self.config['openai'][agent_type]
    
    def get_policy_config(self) -> Dict[str, Any]:
        """Get policy configuration"""
        return self.config.get('policy', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get('logging', {})
    
    def get_config(self) -> Dict[str, Any]:
        """Get entire configuration"""
        return self.config

def get_config_loader(config_path: str = "config.yaml") -> ConfigLoader:
    """
    Get a config loader instance
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        ConfigLoader instance
    """
    return ConfigLoader(config_path)

# For backward compatibility, create a default instance
# but prefer using get_config_loader() function
_default_loader = None

def get_default_loader() -> ConfigLoader:
    """Get the default config loader instance"""
    global _default_loader
    if _default_loader is None:
        # Find the project root directory (where config.yaml is located)
        current_dir = Path.cwd()
        config_path = current_dir / "config.yaml"
        
        # If not found in current directory, look in parent directories
        if not config_path.exists():
            # Look for config.yaml in parent directories (up to 3 levels)
            for i in range(1, 4):
                parent_dir = current_dir.parents[i-1]
                potential_config = parent_dir / "config.yaml"
                if potential_config.exists():
                    config_path = potential_config
                    break
        
        _default_loader = ConfigLoader(str(config_path))
    return _default_loader 