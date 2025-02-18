import logging
import sys

# Create logger instance at module level
_logger = None

def get_logger(name: str = 'FlaskApp') -> logging.Logger:
    """Returns a configured logger instance."""
    global _logger
    if _logger is None:
        # Create new logger
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.INFO)
        
        # Only add handler if none exists
        if not _logger.handlers:
            # Console handler
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            _logger.addHandler(handler)
    
    return _logger