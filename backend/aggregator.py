from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
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
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            logger.info("Database connection established successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def get_session(self):
        return self.Session()

    def cleanup_session(self, session):
        try:
            session.close()
            self.Session.remove()
        except Exception as e:
            logger.error(f"Error cleaning up session: {str(e)}")

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
        session = self.get_session()
        try:
            instance = session.query(model).filter_by(**kwargs).first()
            if instance:
                return instance
            instance = model(**kwargs)
            session.add(instance)
            session.commit()
            logger.debug(f"Created new {model.__name__}: {kwargs}")
            return instance
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error in get_or_create for {model.__name__}: {str(e)}")
            raise
        finally:
            self.cleanup_session(session)

    def validate_timestamp(self, timestamp_value):
        """Validate and convert timestamp to datetime object"""
        try:
            if isinstance(timestamp_value, (int, float)):
                return datetime.fromtimestamp(timestamp_value, tz=timezone.utc)
            elif isinstance(timestamp_value, str):
                try:
                    # Try parsing as float first
                    return datetime.fromtimestamp(float(timestamp_value), tz=timezone.utc)
                except ValueError:
                    # Try parsing as ISO format
                    return datetime.fromisoformat(timestamp_value.replace('Z', '+00:00'))
            elif timestamp_value is None:
                return datetime.now(timezone.utc)
            else:
                raise ValueError(f"Invalid timestamp format: {timestamp_value}")
        except Exception as e:
            logger.warning(f"Invalid timestamp {timestamp_value}, using current time. Error: {str(e)}")
            return datetime.now(timezone.utc)

    def store_metrics(self, metrics_data):
        session = self.get_session()
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

                timestamp = self.validate_timestamp(metric.get('timestamp'))

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
                session.add(measurement)
            
            session.commit()
            logger.info("Successfully stored all metrics")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing metrics: {str(e)}")
            raise
        finally:
            self.cleanup_session(session)

    def get_latest_metrics(self, limit=50):
        session = self.get_session()
        try:
            logger.debug(f"Fetching latest {limit} metrics")
            metrics = session.query(MetricMeasurement)\
                .order_by(MetricMeasurement.timestamp.desc())\
                .limit(limit)\
                .all()
            metrics_list = [metric.to_dict() for metric in metrics]
            logger.info(f"Retrieved {len(metrics_list)} metrics")
            return metrics_list
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error fetching metrics: {str(e)}")
            raise
        finally:
            self.cleanup_session(session)
