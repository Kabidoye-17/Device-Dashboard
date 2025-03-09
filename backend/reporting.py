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

    def get_all_latest_metrics(self, metric_type=None):
        session = self.get_session()
        try:
            # Build the base query with eager loading
            query = session.query(MetricMeasurement)
            query = query.options(joinedload(MetricMeasurement.device).joinedload(Device.details))
            
            # Apply ordering
            query = query.order_by(MetricMeasurement.timestamp_utc.desc())
            
            # Apply metric type filter if provided
            if metric_type:
                query = query.filter(MetricMeasurement.type.has(name=metric_type))
            
            # First check if we have any data
            if query.first() is None:
                logger.warning("No metrics found in the database.")
                return [], 0
                
            # Get the latest timestamp for the 10-minute window
            latest_timestamp = session.query(sa.func.max(MetricMeasurement.timestamp_utc)).scalar()
            ten_minutes_ago = latest_timestamp - timedelta(minutes=10)
            
            # Apply the time filter to the query
            query = query.filter(MetricMeasurement.timestamp_utc >= ten_minutes_ago)
            
            # Get all metrics without pagination
            metrics = query.all()
            
            # Process results
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
            
            total_count = len(measurements)
            logger.info(f"Retrieved all {total_count} metrics for the last 10 minutes")
            return measurements, total_count
        
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error fetching metrics: {str(e)}")
            raise
        finally:
            self.cleanup_session(session)
    def __del__(self):
        self.Session.remove()
