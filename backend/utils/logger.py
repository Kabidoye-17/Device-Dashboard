import logging
import sys
from pathlib import Path

_logger = None

def setup_logger(config, name: str = 'FlaskApp') -> logging.Logger:
    """Configures logger with settings from config"""
    logger = logging.getLogger(name)
    
    if config.logging.console_output.enabled:
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(logging.Formatter(
            config.logging.console_output.format,
            config.logging.console_output.date_format
        ))
        console.setLevel(config.logging.console_output.get_level())
        logger.addHandler(console)
    
    if config.logging.file_output.enabled:
        log_dir = Path(config.logging.file_output.log_dir)
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / config.logging.file_output.filename,
            maxBytes=config.logging.file_output.max_bytes,
            backupCount=config.logging.file_output.backup_count
        )
        file_handler.setFormatter(logging.Formatter(
            config.logging.file_output.format,
            config.logging.file_output.date_format
        ))
        file_handler.setLevel(config.logging.file_output.get_level())
        logger.addHandler(file_handler)
    
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