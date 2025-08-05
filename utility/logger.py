#!/usr/bin/env python3
"""
Unified logging utility for HarmonyGuard_v2 project
Loads configuration from config.yaml and provides consistent logging across all modules
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from .config_loader import get_default_loader

class UnifiedLogger:
    """Unified logging system that loads configuration from config.yaml"""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize the unified logging system"""
        if cls._initialized:
            return
            
        try:
            config_loader = get_default_loader()
            logging_config = config_loader.get_logging_config()
            
            if not logging_config:
                # Fallback to basic configuration
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                cls._initialized = True
                return
            
            # Configure root logger
            root_level = getattr(logging, logging_config.get('level', 'INFO'))
            root_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # Clear any existing handlers
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Configure console handler
            console_config = logging_config.get('console', {})
            if console_config.get('enabled', True):
                console_handler = logging.StreamHandler()
                console_level = getattr(logging, console_config.get('level', 'INFO'))
                console_format = console_config.get('format', root_format)
                console_handler.setLevel(console_level)
                console_handler.setFormatter(logging.Formatter(console_format))
                root_logger.addHandler(console_handler)
            
            # Configure file handler
            file_config = logging_config.get('file', {})
            if file_config.get('enabled', False):
                log_path = Path(file_config.get('path', 'logs'))
                log_path.mkdir(exist_ok=True)
                
                file_handler = logging.handlers.RotatingFileHandler(
                    log_path / 'harmonyguard.log',
                    maxBytes=cls._parse_size(file_config.get('max_size', '10MB')),
                    backupCount=file_config.get('backup_count', 5)
                )
                file_level = getattr(logging, file_config.get('level', 'DEBUG'))
                file_format = file_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
                file_handler.setLevel(file_level)
                file_handler.setFormatter(logging.Formatter(file_format))
                root_logger.addHandler(file_handler)
            
            root_logger.setLevel(root_level)
            cls._initialized = True
            
        except Exception as e:
            # Fallback to basic configuration if anything fails
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger with the specified name
        
        Args:
            name: Logger name (should match the module/file name)
            
        Returns:
            Configured logger instance
        """
        cls.initialize()
        
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        
        # Apply specific configuration for this logger if available
        try:
            config_loader = get_default_loader()
            logging_config = config_loader.get_logging_config()
            logger_configs = logging_config.get('logger_configs', {})
            
            # Find matching config based on logger name
            for config_name, config in logger_configs.items():
                if name.startswith(config_name) or name == config_name:
                    level = getattr(logging, config.get('level', 'INFO'))
                    logger.setLevel(level)
                    break
                    
        except Exception:
            # Use default level if configuration fails
            logger.setLevel(logging.INFO)
        
        cls._loggers[name] = logger
        return logger
    
    @staticmethod
    def _parse_size(size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with automatic name detection
    
    Args:
        name: Optional logger name. If None, will try to detect from calling module
        
    Returns:
        Configured logger instance
    """
    if name is None:
        # Try to detect the calling module name
        import inspect
        frame = inspect.currentframe()
        try:
            # Go up the call stack to find the calling module
            while frame:
                frame = frame.f_back
                if frame and frame.f_globals.get('__name__') != '__main__':
                    module_name = frame.f_globals.get('__name__', 'unknown')
                    # Convert module name to logger name
                    if module_name.startswith('harmony_agents.'):
                        name = module_name.replace('harmony_agents.', 'harmony_agents.')
                    elif module_name.startswith('benchmark.'):
                        name = module_name.replace('benchmark.', 'benchmark.')
                    elif module_name.startswith('utility.'):
                        name = module_name.replace('utility.', 'utility.')
                    else:
                        name = module_name
                    break
        finally:
            del frame
    
    if name is None:
        name = 'unknown'
    
    return UnifiedLogger.get_logger(name) 