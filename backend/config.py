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

@dataclass
class Config:
    SECRET_KEY: str = 'dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    database: DatabaseConfig = DatabaseConfig()
    logging: LoggingConfig = LoggingConfig()

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.database.get_database_url()

def load_config():
    config_path = Path(__file__).parent / 'config.json'
    try:
        if not config_path.exists():
            return Config()  # Return default config if file doesn't exist
            
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            
        return Config(
            database=DatabaseConfig(**config_data.get('database', {})),
            logging=LoggingConfig(**config_data.get('logging', {}))
        )
    except Exception as e:
        logging.warning(f"Failed to load configuration: {str(e)}. Using defaults.")
        return Config()