from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models.db_models import Base, MetricType, Unit, Source, MetricMeasurement
from datetime import datetime, timezone
from utils.logger import get_logger
import sqlalchemy as sa

logger = get_logger(__name__)

class DatabaseAggregator:
    def __init__(self, connection_string):
        try:
            logger.info("Initializing database connection...")
            self.engine = create_engine(connection_string, pool_recycle=280)  # Add pool_recycle for MySQL
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            logger.info("Database connection established successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def verify_connection(self):
        """Verify database connection is working"""
        try:
            with self.engine.connect() as conn:
                conn.execute(sa.text('SELECT 1'))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False

    def get_or_create(self, model, **kwargs):
        try:
            instance = self.session.query(model).filter_by(**kwargs).first()
            if instance:
                return instance
            instance = model(**kwargs)
            self.session.add(instance)
            self.session.commit()
            logger.debug(f"Created new {model.__name__}: {kwargs}")
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error in get_or_create for {model.__name__}: {str(e)}")
            raise

    def store_metrics(self, metrics_data):
        try:
            logger.info(f"Storing {len(metrics_data)} metrics")
            for metric in metrics_data:
                logger.debug(f"Processing metric: {metric}")
                
                # Ensure metric data is properly formatted
                try:
                    metric_value = float(metric['value'])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid metric value: {metric.get('value')}. Skipping.")
                    continue

                # Ensure timestamp is properly formatted
                try:
                    timestamp = datetime.fromtimestamp(float(metric.get('timestamp', datetime.utcnow().timestamp())))
                except (ValueError, TypeError):
                    timestamp = datetime.now(timezone.utc)
                    logger.warning(f"Invalid timestamp, using current time")

                m_type = self.get_or_create(
                    MetricType,
                    name=str(metric.get('type', 'system'))
                )

                unit = self.get_or_create(
                    Unit,
                    unit_name=str(metric.get('unit', 'unknown'))
                )

                source = self.get_or_create(
                    Source,
                    name=str(metric.get('source', 'unknown'))
                )

                measurement = MetricMeasurement(
                    name=str(metric['name']),
                    value=metric_value,
                    type_id=m_type.id,
                    unit_id=unit.id,
                    source_id=source.id,
                    timestamp=timestamp,
                    device_id=str(metric.get('device_id', None))
                )
                self.session.add(measurement)
            
            self.session.commit()
            logger.info("Successfully stored all metrics")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error storing metrics: {str(e)}")
            raise

    def get_latest_metrics(self):
        try:
            logger.debug("Fetching latest metrics")
            metrics = self.session.query(MetricMeasurement).order_by(MetricMeasurement.timestamp.desc()).all()
            metrics_list = [metric.to_dict() for metric in metrics]
            logger.info(f"Retrieved {len(metrics_list)} metrics")
            return metrics_list
        except SQLAlchemyError as e:
            logger.error(f"Error fetching metrics: {str(e)}")
            raise
