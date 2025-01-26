import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class ConsoleLoggingConfig:
    enabled: bool
    level: str
    format: str
    date_format: str

    def get_level(self) -> int:
        import logging
        return getattr(logging, self.level.upper())

@dataclass
class FileLoggingConfig(ConsoleLoggingConfig):
    log_dir: str
    filename: str
    max_bytes: int
    backup_count: int

@dataclass
class LoggingConfig:
    console_output: ConsoleLoggingConfig
    file_output: FileLoggingConfig

def load_config() -> LoggingConfig:
    config_path = Path(__file__).parent / 'config.json'
    with open(config_path, 'r') as f:
        config_data = json.load(f)
        
    raw_logging_config = config_data.get('logging_config', {})
    return LoggingConfig(
        console_output=ConsoleLoggingConfig(**raw_logging_config.get('console_output', {})),
        file_output=FileLoggingConfig(**raw_logging_config.get('file_output', {}))
    ) 