import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import logging

@dataclass
class ConsoleLoggingConfig:
    enabled: bool = True
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'
    level: str = 'INFO'

    def get_level(self) -> int:
        return getattr(logging, self.level.upper())

@dataclass
class FileLoggingConfig:
    enabled: bool = True
    log_dir: str = 'logs'
    filename: str = 'app.log'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'
    level: str = 'DEBUG'
    max_bytes: int = 10_485_760  # 10MB
    backup_count: int = 5

    def get_level(self) -> int:
        return getattr(logging, self.level.upper())

@dataclass
class LoggingConfig:
    console_output: ConsoleLoggingConfig = ConsoleLoggingConfig()
    file_output: FileLoggingConfig = FileLoggingConfig()

def load_config() -> LoggingConfig:
    return LoggingConfig()