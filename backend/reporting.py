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

    def get_latest_metrics(self, metric_type=None, page_number=1, page_size=20):
        if page_number < 1:
            page_number = 1
        
        session = self.get_session()
        try:
            # Get latest timestamp using a more efficient single query
            query = session.query(MetricMeasurement)
            
            # Join tables eagerly to avoid N+1 query problems
            query = query.options(joinedload(MetricMeasurement.device).joinedload(Device.details))
            
            # Apply ordering first to make the query more efficient
            query = query.order_by(MetricMeasurement.timestamp_utc.desc())
            
            # Apply metric type filter if provided
            if metric_type:
                query = query.filter(MetricMeasurement.type.has(name=metric_type))
            
            # Get the first result to determine latest timestamp
            latest_metric = query.first()
            if not latest_metric:
                logger.warning("No metrics found in the database.")
                return [], 0
            
            # Calculate time window based on latest timestamp
            ten_minutes_ago = latest_metric.timestamp_utc - timedelta(minutes=10)
            
            # Apply time filter
            query = query.filter(MetricMeasurement.timestamp_utc >= ten_minutes_ago)
            
            # Count total matching records first - this is more efficient than fetching extra records
            total_count = query.count()
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages
            
            # Apply pagination
            metrics = query.offset((page_number - 1) * page_size).limit(page_size).all()
            
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
            
            logger.info(f"Retrieved {len(measurements)} metrics for page {page_number}")
            return measurements, total_pages
        
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error fetching metrics: {str(e)}")
            raise
        finally:
            self.cleanup_session(session)

    def __del__(self):
        self.Session.remove()
