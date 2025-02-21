import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Union
from config.config import Config

_logger = None

def setup_logger(config: Union[Config, dict], name: str = 'FlaskApp') -> logging.Logger:
    """Configures logger with settings from config"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set base level
    
    # Clear existing handlers
    logger.handlers = []
    
    # Handle both dict and Config object cases
    if isinstance(config, dict):
        console_config = config.get('logging', {}).get('console_output', {})
        file_config = config.get('logging', {}).get('file_output', {})
    else:
        console_config = config.logging.console_output
        file_config = config.logging.file_output
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    ))
    console.setLevel(logging.INFO)
    logger.addHandler(console)
    
    # File handler
    try:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'app.log',
            maxBytes=10_485_760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        ))
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not setup file logging: {e}")
    
    return logger

def get_logger(name: str = 'FlaskApp') -> logging.Logger:
    global _logger
    if _logger is None:
        # Create basic logger until properly configured
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.INFO)
        if not _logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            _logger.addHandler(handler)
    return _logger