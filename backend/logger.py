import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import colorlog
from config import LoggingConfig, ConsoleLoggingConfig, FileLoggingConfig

class LoggerSingleton:
    _instance: Optional['LoggerSingleton'] = None
    _logger: Optional[logging.Logger] = None
    _config: Optional[LoggingConfig] = None

    def __new__(cls) -> 'LoggerSingleton':
        if cls._instance is None:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        self._load_config()
        self._setup_logging()

    def _load_config(self) -> None:
        from config import load_config
        self._config = load_config()

    def _setup_logging(self) -> None:
        if self._config.file_output.enabled:
            log_dir = Path(__file__).parent / self._config.file_output.log_dir
            log_dir.mkdir(exist_ok=True)

        logger = logging.getLogger('FlaskApp')
        logger.handlers.clear()
        logger.setLevel(logging.DEBUG)

        if self._config.console_output.enabled:
            console_handler = logging.StreamHandler()
            console_formatter = colorlog.ColoredFormatter(
                fmt='%(log_color)s' + self._config.console_output.format,
                datefmt=self._config.console_output.date_format,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white'
                }
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(self._config.console_output.get_level())
            logger.addHandler(console_handler)

        if self._config.file_output.enabled:
            file_path = Path(__file__).parent / self._config.file_output.log_dir / self._config.file_output.filename
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=self._config.file_output.max_bytes,
                backupCount=self._config.file_output.backup_count
            )
            file_formatter = logging.Formatter(
                fmt=self._config.file_output.format,
                datefmt=self._config.file_output.date_format
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(self._config.file_output.get_level())
            logger.addHandler(file_handler)

        self._logger = logger

    def get_logger(self) -> logging.Logger:
        return self._logger

def get_logger() -> logging.Logger:
    return LoggerSingleton().get_logger() 