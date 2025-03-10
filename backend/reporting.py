from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sdk.dto import MeasurementDTO
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

    def __enter__(self):
        self.session = self.get_session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if (exc_type):
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.cleanup_session(self.session)

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
        with self as session:
            try:
                query = self._build_base_query(session, metric_type)
                
                if not self._has_metrics(session, query):
                    logger.warning("No metrics found in the database.")
                    return [], 0

                latest_timestamp = self._get_latest_timestamp(session)
                if latest_timestamp is None:
                    logger.warning("No metrics found in the database.")
                    return [], 0

                query = self._apply_time_filter(query, latest_timestamp)
                metrics = query.all()
                
                measurements = self._convert_to_domain_models(metrics)
                total_count = len(measurements)
                logger.info(f"Retrieved all {total_count} metrics for the last 10 minutes")
                return measurements, total_count
            
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error fetching metrics: {str(e)}")
                raise

    def _build_base_query(self, session, metric_type):
        query = session.query(MetricMeasurement)
        query = query.options(joinedload(MetricMeasurement.device).joinedload(Device.details))
        query = query.order_by(MetricMeasurement.timestamp_utc.desc())
        if metric_type:
            query = query.filter(MetricMeasurement.type.has(name=metric_type))
        return query

    def _has_metrics(self, session, query):
        return session.query(query.exists()).scalar()

    def _get_latest_timestamp(self, session):
        return session.query(sa.func.max(MetricMeasurement.timestamp_utc)).scalar()

    def _apply_time_filter(self, query, latest_timestamp):
        ten_minutes_ago = latest_timestamp - timedelta(minutes=10)
        return query.filter(MetricMeasurement.timestamp_utc >= ten_minutes_ago)

    def _convert_to_domain_models(self, metrics):
        return [
            MeasurementDTO(
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