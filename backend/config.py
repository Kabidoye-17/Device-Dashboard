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

@dataclass
class DatabaseConfig:
    username: str = 'Kabidoye17'
    password: str = 'Metricsdbpassword'
    host: str = 'Kabidoye17.mysql.pythonanywhere-services.com'
    name: str = 'Kabidoye17$Metrics'

    def get_database_url(self) -> str:
        return f"mysql+mysqlconnector://{self.username}:{self.password}@{self.host}/{self.name}"

def load_config():
    config_path = Path(__file__).parent / 'config.json'
    try:
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
            
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            
        # Validate required sections
        if 'database' not in config_data or 'logging' not in config_data:
            raise ValueError("Config file missing required sections: 'database' and 'logging'")
            
        return {
            'logging': LoggingConfig(**config_data['logging']),
            'database': DatabaseConfig(**config_data['database'])
        }
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {str(e)}")