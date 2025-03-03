from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from models.db_models import MetricMeasurement
from sqlalchemy.orm import sessionmaker, scoped_session
from utils.logger import get_logger
import sqlalchemy as sa

logger = get_logger(__name__)

class MetricsReporter:
    def __init__(self, connection_string):
        try:
            logger.info("Initializing database connection...")
            self.engine = create_engine(connection_string, pool_recycle=280)  # Add pool_recycle for MySQL
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

    def get_latest_metrics(self, limit=50):
        session = self.get_session()
        try:
            logger.debug(f"Fetching latest {limit} metrics")
            metrics = session.query(MetricMeasurement)\
                .order_by(MetricMeasurement.id.desc())\
                .limit(limit)\
                .all()
            metrics_list = [metric.to_dict() for metric in metrics]
            for metric in metrics_list:
                if isinstance(metric['timestamp_utc'], datetime):  # Ensure it's a datetime object
                    metric['timestamp_utc'] = metric['timestamp_utc'].isoformat()
                    logger.info(f"metric['timestamp_utc'] in get_latest_batch: {metric['timestamp_utc']}")
                    
            logger.info(f"Retrieved {len(metrics_list)} metrics")
            return metrics_list
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error fetching metrics: {str(e)}")
            raise
        finally:
            self.cleanup_session(session)


    def __del__(self):
        self.session.close()
