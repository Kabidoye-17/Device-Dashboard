import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict
import logging

@dataclass
class ConsoleLoggingConfig:
    enabled: bool
    format: str
    date_format: str
    level: str

    def get_level(self) -> int:
        return getattr(logging, self.level.upper())

@dataclass
class FileLoggingConfig:
    enabled: bool
    log_dir: str
    filename: str
    format: str
    date_format: str
    level: str
    max_bytes: int
    backup_count: int

    def get_level(self) -> int:
        return getattr(logging, self.level.upper())

@dataclass
class LoggingConfig:
    console_output: ConsoleLoggingConfig
    file_output: FileLoggingConfig

@dataclass
class DatabaseConfig:
    username: str
    password: str
    host: str
    name: str

    def get_database_url(self) -> str:
        return f"mysql+mysqlconnector://{self.username}:{self.password}@{self.host}/{self.name}"

@dataclass
class MetricConfig:
    name: str
    unit: str
    format: Optional[Dict[str, str]] = None

@dataclass
class SystemMetricsConfig:
    cpu_load: MetricConfig
    ram_usage: MetricConfig
    network_sent: MetricConfig

@dataclass
class CryptoMetricsConfig:
    price: MetricConfig
    bid: MetricConfig
    ask: MetricConfig

@dataclass
class TransformRulesConfig:
    system: SystemMetricsConfig
    crypto: CryptoMetricsConfig

    def __post_init__(self):
        if isinstance(self.system, dict):
            self.system = SystemMetricsConfig(**{
                k: MetricConfig(**v) for k, v in self.system.items()
            })
        if isinstance(self.crypto, dict):
            self.crypto = CryptoMetricsConfig(**{
                k: MetricConfig(**v) for k, v in self.crypto.items()
            })

@dataclass
class ServerConfig:
    url: str
    timeout: int
    collect_upload_interval: int
    max_queue_size: int
    batch_size: int
    polling_endpoint: str
    polling_interval: int
    api_metrics_endpoint: str

@dataclass
class CryptoCollectorConfig:
    currency_pairs: list
    base_url: str
    collector: str
    device_id: str
    ticker_endpoint: str
    device_name: str

@dataclass
class CollectorTypesConfig:
    system: str
    crypto: str

@dataclass
class Config:
    SECRET_KEY: str
    SQLALCHEMY_TRACK_MODIFICATIONS: bool
    database: DatabaseConfig
    logging: LoggingConfig
    transform_rules: TransformRulesConfig
    server: ServerConfig
    crypto_collector: CryptoCollectorConfig
    collector_types: CollectorTypesConfig

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.database.get_database_url()

def load_config():
    config_path = Path(__file__).parent / 'config.json'
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        db_username = os.getenv("DB_USERNAME", config_data['database']['username'])
        db_password = os.getenv("DB_PASSWORD", config_data['database']['password'])

        return Config(
            SECRET_KEY=config_data.get('SECRET_KEY', ''),
            SQLALCHEMY_TRACK_MODIFICATIONS=config_data.get('SQLALCHEMY_TRACK_MODIFICATIONS', False),
            database=DatabaseConfig(
                username=db_username,
                password=db_password,
                host=config_data['database']['host'],
                name=config_data['database']['name']
            ),
            logging=LoggingConfig(
                console_output=ConsoleLoggingConfig(**config_data['logging']['console_output']),
                file_output=FileLoggingConfig(**config_data['logging']['file_output'])
            ),
            transform_rules=TransformRulesConfig(**config_data['transform_rules']),
            server=ServerConfig(**config_data['server']),
            crypto_collector=CryptoCollectorConfig(**config_data['crypto_collector']),
            collector_types=CollectorTypesConfig(**config_data['collector_types']),
        )
    except Exception as e:
        logging.error(f"Failed to load configuration: {str(e)}")
        raise