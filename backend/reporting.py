from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from models.measurement import Measurement
from models.db_models import MetricMeasurement
from models.db_models import Device
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from utils.logger import get_logger
import sqlalchemy as sa

logger = get_logger(__name__)

class MetricsReporter:
    def __init__(self, connection_string):
        try:
            logger.info("Initializing database connection...")
            self.engine = create_engine(connection_string, pool_recycle=280, pool_size=5, max_overflow=10)  # Add pool_recycle and pool_size
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

    def get_latest_metrics(self, metric_type=None):
        session = self.get_session()
        try:
            # Get the most recent timestamp from the database
            latest_timestamp = session.query(sa.func.max(MetricMeasurement.timestamp_utc)).scalar()
            if not latest_timestamp:
                logger.warning("No metrics found in the database.")
                return []

            ten_minutes_ago = latest_timestamp - timedelta(minutes=10)
            logger.debug(f"Fetching metrics from the last 10 minutes based on the latest timestamp: {latest_timestamp.isoformat()}")

            query = (
                session.query(MetricMeasurement)
                .options(joinedload(MetricMeasurement.device).joinedload(Device.details))
                .filter(MetricMeasurement.timestamp_utc >= ten_minutes_ago)  # Filtering by time
            )

            if metric_type:
                query = query.filter(MetricMeasurement.type == metric_type)

            metrics = query.order_by(MetricMeasurement.timestamp_utc.desc()).all()

            measurements = [
                Measurement(
                    device_id=metric.device.device_id,
                    device_name=metric.device.details.device_name,
                    name=metric.name,
                    value=metric.value,
                    type=metric.type.name,
                    unit=metric.unit.unit_name,
                    timestamp_utc=metric.timestamp_utc.isoformat(),
                    utc_offset=metric.utc_offset,
                ).serialize()
                for metric in metrics
            ]

            logger.info(f"Retrieved {len(measurements)} metrics from the last 10 minutes")
            return measurements

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error fetching metrics: {str(e)}")
            raise
        finally:
            self.cleanup_session(session)

    def __del__(self):
        self.Session.remove()
